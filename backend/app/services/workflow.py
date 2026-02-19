"""
RIS Workflow Service

Handles parliamentary workflows:
- Paper lifecycle (draft -> submitted -> deliberation -> decided -> published)
- Meeting lifecycle (planned -> invited -> running -> completed)
- Voting and resolution tracking
- Agenda management
"""
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.oparl import (
    Paper, Meeting, AgendaItem, Consultation, Organization, Person, File
)


# Paper status workflow
PAPER_TRANSITIONS = {
    'draft': ['submitted', 'withdrawn'],
    'submitted': ['deliberation', 'withdrawn'],
    'deliberation': ['decided', 'deferred', 'withdrawn'],
    'decided': ['published'],
    'deferred': ['deliberation', 'withdrawn'],
    'published': [],
    'withdrawn': [],
}

# Meeting status workflow
MEETING_TRANSITIONS = {
    'scheduled': ['invited', 'cancelled'],
    'invited': ['running', 'cancelled'],
    'running': ['completed'],
    'completed': [],
    'cancelled': [],
}


class WorkflowService:
    def __init__(self, session: Session):
        self.session = session

    # ========================================
    # Paper Workflows
    # ========================================
    def create_paper(
        self,
        body_id: str,
        tenant_id: str,
        name: str,
        paper_type: str,
        reference: Optional[str] = None,
        originator_person_ids: List[str] = None,
        originator_org_ids: List[str] = None,
    ) -> Paper:
        """Create a new paper (Drucksache/Vorlage)."""
        paper = Paper(
            body_id=body_id,
            tenant_id=tenant_id,
            name=name,
            paper_type=paper_type,
            reference=reference or self._generate_reference(body_id, paper_type),
            date=date.today(),
        )
        self.session.add(paper)
        self.session.flush()

        # Add originators
        if originator_person_ids:
            persons = self.session.query(Person).filter(
                Person.id.in_(originator_person_ids)
            ).all()
            for p in persons:
                paper.originator_persons.append(p)

        if originator_org_ids:
            orgs = self.session.query(Organization).filter(
                Organization.id.in_(originator_org_ids)
            ).all()
            for o in orgs:
                paper.originator_organizations.append(o)

        self.session.commit()
        return paper

    def _generate_reference(self, body_id: str, paper_type: str) -> str:
        """Generate paper reference number: DS/YYYY/NNN."""
        year = date.today().year
        count = self.session.query(Paper).filter(
            Paper.body_id == body_id,
            Paper.date >= date(year, 1, 1),
        ).count()
        
        prefix_map = {
            'Vorlage': 'V',
            'Antrag': 'A',
            'Anfrage': 'AF',
            'Beschlussvorlage': 'BV',
            'Mitteilung': 'M',
            'Stellungnahme': 'SN',
            'Bericht': 'B',
        }
        prefix = prefix_map.get(paper_type, 'DS')
        return f"{prefix}/{year}/{count + 1:03d}"

    # ========================================
    # Meeting Workflows
    # ========================================
    def create_meeting(
        self,
        body_id: str,
        tenant_id: str,
        name: str,
        organization_id: str,
        start: datetime,
        end: Optional[datetime] = None,
        location_id: Optional[str] = None,
    ) -> Meeting:
        """Create a new meeting (Sitzung)."""
        meeting = Meeting(
            body_id=body_id,
            tenant_id=tenant_id,
            name=name,
            organization_id=organization_id,
            meeting_state='scheduled',
            start=start,
            end=end,
            location_id=location_id,
        )
        self.session.add(meeting)
        self.session.commit()
        return meeting

    def change_meeting_state(self, meeting_id: str, new_state: str) -> Meeting:
        """Change meeting status with transition validation."""
        meeting = self.session.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise ValueError("Sitzung nicht gefunden")

        allowed = MEETING_TRANSITIONS.get(meeting.meeting_state, [])
        if new_state not in allowed:
            raise ValueError(
                f"Ungueltige Statusaenderung: {meeting.meeting_state} -> {new_state}. "
                f"Erlaubt: {allowed}"
            )

        meeting.meeting_state = new_state
        meeting.modified = datetime.utcnow()
        self.session.commit()
        return meeting

    # ========================================
    # Agenda Management
    # ========================================
    def add_agenda_item(
        self,
        meeting_id: str,
        tenant_id: str,
        name: str,
        number: Optional[str] = None,
        public: bool = True,
        paper_id: Optional[str] = None,
    ) -> AgendaItem:
        """Add an agenda item (TOP) to a meeting."""
        # Get next order number
        max_order = self.session.query(AgendaItem).filter(
            AgendaItem.meeting_id == meeting_id
        ).count()

        item = AgendaItem(
            meeting_id=meeting_id,
            tenant_id=tenant_id,
            name=name,
            number=number or f"TOP {max_order + 1}",
            order=max_order + 1,
            public=public,
        )
        self.session.add(item)
        self.session.flush()

        # Create consultation if paper is linked
        if paper_id:
            meeting = self.session.query(Meeting).filter(Meeting.id == meeting_id).first()
            consultation = Consultation(
                paper_id=paper_id,
                agenda_item_id=item.id,
                tenant_id=tenant_id,
                organization_id=meeting.organization_id if meeting else None,
            )
            self.session.add(consultation)

        self.session.commit()
        return item

    def reorder_agenda(self, meeting_id: str, item_ids: List[str]) -> List[AgendaItem]:
        """Reorder agenda items."""
        items = self.session.query(AgendaItem).filter(
            AgendaItem.meeting_id == meeting_id,
            AgendaItem.id.in_(item_ids),
        ).all()

        item_map = {item.id: item for item in items}
        for i, item_id in enumerate(item_ids):
            if item_id in item_map:
                item_map[item_id].order = i + 1
                item_map[item_id].number = f"TOP {i + 1}"

        self.session.commit()
        return sorted(items, key=lambda x: x.order)

    def set_resolution(
        self,
        agenda_item_id: str,
        result: str,
        resolution_text: Optional[str] = None,
        resolution_file_id: Optional[str] = None,
    ) -> AgendaItem:
        """Record a resolution/vote result for an agenda item."""
        item = self.session.query(AgendaItem).filter(
            AgendaItem.id == agenda_item_id
        ).first()
        if not item:
            raise ValueError("TOP nicht gefunden")

        item.result = result
        item.resolution_text = resolution_text
        item.resolution_file_id = resolution_file_id
        item.modified = datetime.utcnow()
        self.session.commit()
        return item

    # ========================================
    # Search
    # ========================================
    def search_papers(
        self,
        tenant_id: str,
        body_id: str,
        query: Optional[str] = None,
        paper_type: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple:
        """Search papers with filters."""
        q = self.session.query(Paper).filter(
            Paper.tenant_id == tenant_id,
            Paper.body_id == body_id,
            Paper.deleted == False,
        )

        if query:
            q = q.filter(Paper.name.ilike(f"%{query}%"))
        if paper_type:
            q = q.filter(Paper.paper_type == paper_type)
        if date_from:
            q = q.filter(Paper.date >= date_from)
        if date_to:
            q = q.filter(Paper.date <= date_to)

        total = q.count()
        papers = q.order_by(Paper.date.desc()).offset(offset).limit(limit).all()
        return papers, total
