"""
aitema|RIS - Demo-Daten-Generator

Erstellt eine Musterkommune "Musterstadt" mit:
- 1 Body (Gemeinderat Musterstadt)
- 5 Organizations (SPD-Fraktion, CDU-Fraktion, Gruene-Fraktion, Hauptausschuss, Bauausschuss)
- 10 Persons (fiktive Mandatstraeger mit Fraktionszugehoerigkeit)
- 5 Meetings (vergangene + kommende Sitzungen)
- 10 Papers (Vorlagen, Antraege verschiedener Typen)
- AgendaItems fuer jede Sitzung
"""
from datetime import datetime, date, timedelta
import uuid

from sqlalchemy.orm import Session

from app.models.oparl import (
    OParlSystem, Body, Organization, Person, Membership,
    Meeting, AgendaItem, Paper, Consultation, LegislativeTerm,
)


def _id() -> str:
    return str(uuid.uuid4())


def seed_musterstadt(db: Session) -> dict:
    """
    Kompletten Datensatz fuer die Musterstadt anlegen.
    Returns: Dict mit Anzahl erstellter Objekte.
    """
    tenant = "musterstadt"
    today = date.today()
    counts = {}

    # ========================================
    # System
    # ========================================
    system = db.query(OParlSystem).first()
    if not system:
        system = OParlSystem(
            id=_id(),
            name="aitema|Rats",
            oparl_version="https://schema.oparl.org/1.1/",
            vendor="https://aitema.de",
            product="https://aitema.de/rats",
        )
        db.add(system)
        db.flush()

    # ========================================
    # Body
    # ========================================
    body = Body(
        id=_id(),
        tenant_id=tenant,
        name="Gemeinderat Musterstadt",
        short_name="Musterstadt",
        body_type="Gemeinde",
        ags="12345678",
        rgs="123456780000",
        contact_email="rat@musterstadt.de",
        web="https://musterstadt.de",
    )
    db.add(body)
    db.flush()
    counts["bodies"] = 1

    # ========================================
    # Wahlperiode
    # ========================================
    leg_term = LegislativeTerm(
        id=_id(),
        tenant_id=tenant,
        body_id=body.id,
        name="Wahlperiode 2024-2029",
        start_date=date(2024, 9, 1),
        end_date=date(2029, 8, 31),
    )
    db.add(leg_term)
    db.flush()

    # ========================================
    # Organizations (Fraktionen + Ausschuesse)
    # ========================================
    org_data = [
        {"name": "SPD-Fraktion", "short": "SPD", "type": "Fraktion", "cls": "Fraktion"},
        {"name": "CDU-Fraktion", "short": "CDU", "type": "Fraktion", "cls": "Fraktion"},
        {"name": "Buendnis 90/Die Gruenen-Fraktion", "short": "Gruene", "type": "Fraktion", "cls": "Fraktion"},
        {"name": "Hauptausschuss", "short": "HA", "type": "Ausschuss", "cls": "Gremium"},
        {"name": "Bauausschuss", "short": "BA", "type": "Ausschuss", "cls": "Gremium"},
    ]

    orgs = {}
    for od in org_data:
        org = Organization(
            id=_id(),
            tenant_id=tenant,
            body_id=body.id,
            name=od["name"],
            short_name=od["short"],
            organization_type=od["type"],
            classification=od["cls"],
            start_date=date(2024, 9, 1),
        )
        db.add(org)
        orgs[od["short"]] = org

    db.flush()
    counts["organizations"] = len(orgs)

    # ========================================
    # Persons (Mandatstraeger)
    # ========================================
    person_data = [
        {"given": "Maria", "family": "Schmidt", "frak": "SPD", "addr": "Herr", "gender": "female"},
        {"given": "Thomas", "family": "Mueller", "frak": "SPD", "addr": "Herr", "gender": "male"},
        {"given": "Sabine", "family": "Weber", "frak": "SPD", "addr": "Frau", "gender": "female"},
        {"given": "Klaus", "family": "Fischer", "frak": "CDU", "addr": "Herr", "gender": "male"},
        {"given": "Andrea", "family": "Wagner", "frak": "CDU", "addr": "Frau", "gender": "female"},
        {"given": "Peter", "family": "Becker", "frak": "CDU", "addr": "Herr", "gender": "male"},
        {"given": "Claudia", "family": "Hoffmann", "frak": "Gruene", "addr": "Frau", "gender": "female"},
        {"given": "Stefan", "family": "Koch", "frak": "Gruene", "addr": "Herr", "gender": "male"},
        {"given": "Erika", "family": "Braun", "frak": "SPD", "addr": "Frau", "gender": "female"},
        {"given": "Wolfgang", "family": "Richter", "frak": "CDU", "addr": "Herr", "gender": "male"},
    ]

    persons = []
    for pd in person_data:
        person = Person(
            id=_id(),
            tenant_id=tenant,
            body_id=body.id,
            name=f"{pd[given]} {pd[family]}",
            given_name=pd["given"],
            family_name=pd["family"],
            form_of_address=pd["addr"],
            gender=pd["gender"],
        )
        db.add(person)
        persons.append((person, pd["frak"]))

    db.flush()
    counts["persons"] = len(persons)

    # Memberships
    membership_count = 0
    for person, frak_key in persons:
        # Fraktionsmitgliedschaft
        mem = Membership(
            id=_id(),
            tenant_id=tenant,
            person_id=person.id,
            organization_id=orgs[frak_key].id,
            role="Mitglied",
            start_date=date(2024, 9, 1),
        )
        db.add(mem)
        membership_count += 1

    # Vorsitzende
    chair_mem = Membership(
        id=_id(),
        tenant_id=tenant,
        person_id=persons[0][0].id,  # Maria Schmidt
        organization_id=orgs["HA"].id,
        role="Vorsitzende",
        start_date=date(2024, 9, 1),
    )
    db.add(chair_mem)
    membership_count += 1

    chair_ba = Membership(
        id=_id(),
        tenant_id=tenant,
        person_id=persons[3][0].id,  # Klaus Fischer
        organization_id=orgs["BA"].id,
        role="Vorsitzender",
        start_date=date(2024, 9, 1),
    )
    db.add(chair_ba)
    membership_count += 1

    db.flush()
    counts["memberships"] = membership_count

    # ========================================
    # Meetings (vergangene + kommende)
    # ========================================
    meeting_data = [
        {
            "name": "42. Sitzung des Gemeinderats",
            "org": "HA",
            "start": datetime.combine(today - timedelta(days=60), datetime.min.time().replace(hour=18)),
            "state": "completed",
        },
        {
            "name": "15. Sitzung des Bauausschusses",
            "org": "BA",
            "start": datetime.combine(today - timedelta(days=30), datetime.min.time().replace(hour=17)),
            "state": "completed",
        },
        {
            "name": "43. Sitzung des Gemeinderats",
            "org": "HA",
            "start": datetime.combine(today - timedelta(days=7), datetime.min.time().replace(hour=18)),
            "state": "completed",
        },
        {
            "name": "16. Sitzung des Bauausschusses",
            "org": "BA",
            "start": datetime.combine(today + timedelta(days=14), datetime.min.time().replace(hour=17)),
            "state": "invited",
        },
        {
            "name": "44. Sitzung des Gemeinderats",
            "org": "HA",
            "start": datetime.combine(today + timedelta(days=28), datetime.min.time().replace(hour=18)),
            "state": "scheduled",
        },
    ]

    meetings = []
    for md in meeting_data:
        meeting = Meeting(
            id=_id(),
            tenant_id=tenant,
            body_id=body.id,
            name=md["name"],
            organization_id=orgs[md["org"]].id,
            meeting_state=md["state"],
            start=md["start"],
            end=md["start"] + timedelta(hours=2),
            cancelled=False,
        )
        db.add(meeting)
        meetings.append(meeting)

    db.flush()
    counts["meetings"] = len(meetings)

    # ========================================
    # Papers (Vorlagen, Antraege)
    # ========================================
    year = today.year
    paper_data = [
        {"name": "Haushaltssatzung {y}".format(y=year), "type": "Beschlussvorlage", "ref": f"BV/{year}/001"},
        {"name": "Bebauungsplan Nr. 42 Am Waldrand", "type": "Vorlage", "ref": f"V/{year}/002"},
        {"name": "Antrag auf Erweiterung der Kita Sonnenschein", "type": "Antrag", "ref": f"A/{year}/003"},
        {"name": "Sachstandsbericht Digitalisierung", "type": "Bericht", "ref": f"B/{year}/004"},
        {"name": "Anfrage zur Verkehrsberuhigung Schulstrasse", "type": "Anfrage", "ref": f"AF/{year}/005"},
        {"name": "Beschlussvorlage Sanierung Turnhalle", "type": "Beschlussvorlage", "ref": f"BV/{year}/006"},
        {"name": "Antrag: Kostenloser OEPNV fuer Schueler", "type": "Antrag", "ref": f"A/{year}/007"},
        {"name": "Mitteilung: Foerderbescheid Breitbandausbau", "type": "Mitteilung", "ref": f"M/{year}/008"},
        {"name": "Stellungnahme zum Regionalplan 2030", "type": "Stellungnahme", "ref": f"SN/{year}/009"},
        {"name": "Antrag auf Einrichtung eines Jugendparlaments", "type": "Antrag", "ref": f"A/{year}/010"},
    ]

    papers = []
    for i, ppd in enumerate(paper_data):
        paper = Paper(
            id=_id(),
            tenant_id=tenant,
            body_id=body.id,
            name=ppd["name"],
            paper_type=ppd["type"],
            reference=ppd["ref"],
            date=today - timedelta(days=90 - i * 9),
        )
        db.add(paper)
        papers.append(paper)

    db.flush()
    counts["papers"] = len(papers)

    # ========================================
    # AgendaItems + Consultations
    # ========================================
    agenda_count = 0
    consultation_count = 0

    # Vergangene Sitzungen: mit Ergebnissen
    for m_idx, meeting in enumerate(meetings[:3]):
        # Standard-TOPs
        tops = [
            {"name": "Eroeffnung und Begruessung", "num": "TOP 1", "pub": True},
            {"name": "Genehmigung der Niederschrift", "num": "TOP 2", "pub": True},
            {"name": "Mitteilungen der Verwaltung", "num": "TOP 3", "pub": True},
        ]

        # 2-3 Paper-TOPs pro Sitzung
        paper_start = m_idx * 3
        for p_idx in range(min(3, len(papers) - paper_start)):
            p = papers[paper_start + p_idx]
            tops.append({
                "name": p.name,
                "num": f"TOP {4 + p_idx}",
                "pub": True,
                "paper": p,
            })

        tops.append({"name": "Verschiedenes", "num": f"TOP {len(tops) + 1}", "pub": True})

        for order, top_data in enumerate(tops, 1):
            ai = AgendaItem(
                id=_id(),
                tenant_id=tenant,
                meeting_id=meeting.id,
                name=top_data["name"],
                number=top_data["num"],
                order=order,
                public=top_data["pub"],
                result="angenommen" if "paper" in top_data else None,
                resolution_text="Einstimmig beschlossen" if "paper" in top_data else None,
            )
            db.add(ai)
            agenda_count += 1

            if "paper" in top_data:
                cons = Consultation(
                    id=_id(),
                    tenant_id=tenant,
                    paper_id=top_data["paper"].id,
                    agenda_item_id=ai.id,
                    organization_id=meeting.organization_id,
                )
                db.add(cons)
                consultation_count += 1

    # Kommende Sitzungen: ohne Ergebnis
    for meeting in meetings[3:]:
        remaining_papers = papers[6:]  # Letzte Papers
        tops = [
            {"name": "Eroeffnung und Begruessung", "num": "TOP 1", "pub": True},
            {"name": "Genehmigung der Niederschrift", "num": "TOP 2", "pub": True},
        ]
        for p_idx, p in enumerate(remaining_papers[:3]):
            tops.append({
                "name": p.name,
                "num": f"TOP {3 + p_idx}",
                "pub": True,
                "paper": p,
            })
        tops.append({"name": "Verschiedenes", "num": f"TOP {len(tops) + 1}", "pub": True})

        for order, top_data in enumerate(tops, 1):
            ai = AgendaItem(
                id=_id(),
                tenant_id=tenant,
                meeting_id=meeting.id,
                name=top_data["name"],
                number=top_data["num"],
                order=order,
                public=top_data["pub"],
            )
            db.add(ai)
            agenda_count += 1

            if "paper" in top_data:
                cons = Consultation(
                    id=_id(),
                    tenant_id=tenant,
                    paper_id=top_data["paper"].id,
                    agenda_item_id=ai.id,
                    organization_id=meeting.organization_id,
                )
                db.add(cons)
                consultation_count += 1

    db.flush()
    counts["agenda_items"] = agenda_count
    counts["consultations"] = consultation_count

    db.commit()

    return counts
