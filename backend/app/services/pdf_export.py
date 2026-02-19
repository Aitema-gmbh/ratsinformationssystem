"""
PDF Export Service for aitema|Rats

Generates HTML templates for PDF conversion via wkhtmltopdf.
Each function returns an HTML string ready for PDF rendering.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.oparl import Meeting, Paper, AgendaItem, Consultation


_BASE_STYLES = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
        font-size: 10pt;
        line-height: 1.5;
        color: #111827;
        padding: 20mm;
    }
    .header {
        border-bottom: 3px solid #1e3a5f;
        padding-bottom: 12pt;
        margin-bottom: 16pt;
    }
    .header h1 {
        font-size: 16pt;
        color: #1e3a5f;
        margin-bottom: 4pt;
    }
    .header .subtitle {
        font-size: 11pt;
        color: #4b5563;
    }
    .meta-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 16pt;
        font-size: 9pt;
    }
    .meta-table td {
        padding: 4pt 8pt;
        border-bottom: 1px solid #e5e7eb;
    }
    .meta-table td:first-child {
        font-weight: 600;
        color: #374151;
        width: 140pt;
    }
    h2 {
        font-size: 12pt;
        color: #1e3a5f;
        border-bottom: 1px solid #d1d5db;
        padding-bottom: 4pt;
        margin: 16pt 0 8pt;
    }
    table.data {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 12pt;
        font-size: 9pt;
    }
    table.data th {
        background: #f3f4f6;
        padding: 6pt 8pt;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #d1d5db;
    }
    table.data td {
        padding: 5pt 8pt;
        border-bottom: 1px solid #e5e7eb;
    }
    .agenda-item {
        margin-bottom: 8pt;
        padding: 6pt 8pt;
        border-left: 3px solid #1e3a5f;
        background: #f9fafb;
    }
    .agenda-item .number {
        font-weight: 700;
        color: #1e3a5f;
    }
    .agenda-item .reference {
        font-size: 8pt;
        color: #6b7280;
        margin-left: 8pt;
    }
    .agenda-item .non-public {
        font-size: 8pt;
        color: #dc2626;
        font-style: italic;
    }
    .resolution {
        margin: 4pt 0 4pt 16pt;
        padding: 4pt 8pt;
        background: #ecfdf5;
        border-left: 2px solid #16a34a;
        font-size: 9pt;
    }
    .vote-result {
        font-size: 8pt;
        color: #374151;
    }
    .footer {
        position: fixed;
        bottom: 10mm;
        left: 20mm;
        right: 20mm;
        border-top: 1px solid #d1d5db;
        padding-top: 6pt;
        font-size: 7pt;
        color: #9ca3af;
        display: flex;
        justify-content: space-between;
    }
    .attendance-present { color: #16a34a; }
    .attendance-absent { color: #dc2626; }
    @media print {
        body { padding: 0; }
        .page-break { page-break-before: always; }
    }
</style>
"""


def _html_escape(text):
    if not text:
        return ""
    return (
        str(text).replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _format_date(dt):
    if not dt:
        return ""
    if isinstance(dt, datetime):
        return dt.strftime("%d.%m.%Y %H:%M Uhr")
    return dt.strftime("%d.%m.%Y")


def _footer_html():
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    return (
        '<div class="footer">'
        f'<span>Generiert aus aitema|Rats - {now}</span>'
        '<span>https://aitema.de</span>'
        '</div>'
    )


def generate_tagesordnung_pdf(meeting):
    """Generate HTML for meeting agenda PDF."""
    org_name = ""
    if meeting.organization:
        org_name = meeting.organization.name or ""
    meeting_name = meeting.name or "Sitzung"

    location_str = ""
    if meeting.location:
        parts = []
        if meeting.location.description:
            parts.append(_html_escape(meeting.location.description))
        if meeting.location.room:
            parts.append("Raum: " + _html_escape(meeting.location.room))
        if meeting.location.street_address:
            parts.append(_html_escape(meeting.location.street_address))
        if meeting.location.locality:
            parts.append(_html_escape(meeting.location.locality))
        location_str = ", ".join(parts)

    agenda_items = sorted(meeting.agenda_items, key=lambda a: a.order)

    agenda_html = ""
    for item in agenda_items:
        number = _html_escape(item.number or str(item.order))
        name = _html_escape(item.name or "Ohne Titel")
        public_marker = ""
        if not item.public:
            public_marker = ' <span class="non-public">(nichtoeffentlich)</span>'

        reference = ""
        if item.consultation and item.consultation.paper:
            paper = item.consultation.paper
            ref = _html_escape(paper.reference or paper.name or "")
            reference = f'<span class="reference">Vorlage: {ref}</span>'

        agenda_html += (
            '<div class="agenda-item">'
            f'<span class="number">TOP {number}:</span> {name}{public_marker}<br/>'
            f'{reference}'
            '</div>'
        )

    html = (
        '<!DOCTYPE html>'
        '<html lang="de"><head><meta charset="UTF-8">'
        f'<title>Tagesordnung - {_html_escape(meeting_name)}</title>'
        f'{_BASE_STYLES}'
        '</head><body>'
        '<div class="header">'
        '<h1>Tagesordnung</h1>'
        f'<div class="subtitle">{_html_escape(org_name)} - {_html_escape(meeting_name)}</div>'
        '</div>'
        '<table class="meta-table">'
        f'<tr><td>Gremium</td><td>{_html_escape(org_name)}</td></tr>'
        f'<tr><td>Datum / Uhrzeit</td><td>{_format_date(meeting.start)}'
    )
    if meeting.end:
        html += f' - {_format_date(meeting.end)}'
    html += '</td></tr>'
    html += f'<tr><td>Ort</td><td>{location_str or "Nicht angegeben"}</td></tr>'
    html += f'<tr><td>Status</td><td>{_html_escape(meeting.meeting_state or "")}</td></tr>'
    html += '</table>'
    html += f'<h2>Tagesordnung ({len(agenda_items)} Punkte)</h2>'
    if agenda_html:
        html += agenda_html
    else:
        html += '<p style="color: #9ca3af;">Keine Tagesordnungspunkte vorhanden.</p>'
    html += _footer_html()
    html += '</body></html>'
    return html


def generate_vorlage_pdf(paper):
    """Generate HTML for Paper/Vorlage PDF."""
    paper_name = _html_escape(paper.name or "Vorlage")
    reference = _html_escape(paper.reference or "")
    paper_type = _html_escape(paper.paper_type or "")

    originators = []
    try:
        for p in paper.originator_persons:
            display = p.name or ((p.given_name or "") + " " + (p.family_name or "")).strip()
            originators.append(_html_escape(display))
    except Exception:
        pass
    try:
        for o in paper.originator_organizations:
            originators.append(_html_escape(o.name or ""))
    except Exception:
        pass
    originator_str = ", ".join(originators) if originators else "Nicht angegeben"

    consultations_html = ""
    try:
        consultations = list(paper.consultations)
        if consultations:
            rows = ""
            for c in consultations:
                c_org = _html_escape(c.organization.name) if c.organization else ""
                c_role = _html_escape(c.role or "")
                c_auth = "Ja" if c.authoritative else "Nein"
                c_result = ""
                if c.agenda_item and c.agenda_item.result:
                    c_result = _html_escape(c.agenda_item.result)
                rows += (
                    f'<tr><td>{c_org}</td><td>{c_role}</td>'
                    f'<td>{c_auth}</td><td>{c_result}</td></tr>'
                )
            consultations_html = (
                '<h2>Beratungsfolge</h2>'
                '<table class="data"><thead><tr>'
                '<th>Gremium</th><th>Rolle</th><th>Federfuehrend</th><th>Ergebnis</th>'
                '</tr></thead><tbody>' + rows + '</tbody></table>'
            )
    except Exception:
        pass

    main_file_info = ""
    if paper.main_file:
        main_file_info = (
            f'<tr><td>Hauptdokument</td>'
            f'<td>{_html_escape(paper.main_file.file_name or "Dokument")}</td></tr>'
        )

    html = (
        '<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">'
        f'<title>Vorlage - {reference or paper_name}</title>'
        f'{_BASE_STYLES}</head><body>'
        '<div class="header">'
        f'<h1>{paper_type or "Vorlage"}</h1>'
        f'<div class="subtitle">{reference} - {paper_name}</div>'
        '</div>'
        '<table class="meta-table">'
        f'<tr><td>Aktenzeichen</td><td>{reference or "Nicht vergeben"}</td></tr>'
        f'<tr><td>Typ</td><td>{paper_type or "Nicht angegeben"}</td></tr>'
        f'<tr><td>Datum</td><td>{_format_date(paper.date)}</td></tr>'
        f'<tr><td>Einreicher</td><td>{originator_str}</td></tr>'
        f'{main_file_info}'
        '</table>'
        f'{consultations_html}'
        f'{_footer_html()}'
        '</body></html>'
    )
    return html


def generate_sitzungsprotokoll_pdf(meeting):
    """Generate HTML for meeting protocol PDF."""
    org_name = ""
    if meeting.organization:
        org_name = meeting.organization.name or ""
    meeting_name = meeting.name or "Sitzung"

    location_str = ""
    if meeting.location:
        parts = []
        if meeting.location.description:
            parts.append(_html_escape(meeting.location.description))
        if meeting.location.room:
            parts.append("Raum: " + _html_escape(meeting.location.room))
        if meeting.location.street_address:
            parts.append(_html_escape(meeting.location.street_address))
        location_str = ", ".join(parts)

    attendance_html = ""
    try:
        participants = list(meeting.participants)
        if participants:
            rows = ""
            for person in participants:
                display = person.name or ((person.given_name or "") + " " + (person.family_name or "")).strip()
                rows += (
                    f'<tr><td>{_html_escape(display)}</td>'
                    '<td class="attendance-present">anwesend</td></tr>'
                )
            attendance_html = (
                f'<h2>Anwesenheit ({len(participants)} Teilnehmer)</h2>'
                '<table class="data"><thead><tr><th>Name</th><th>Status</th></tr></thead>'
                f'<tbody>{rows}</tbody></table>'
            )
    except Exception:
        pass

    agenda_items = sorted(meeting.agenda_items, key=lambda a: a.order)
    tops_html = ""
    for item in agenda_items:
        number = _html_escape(item.number or str(item.order))
        name = _html_escape(item.name or "Ohne Titel")
        public_marker = ""
        if not item.public:
            public_marker = ' <span class="non-public">(nichtoeffentlich)</span>'

        paper_ref = ""
        if item.consultation and item.consultation.paper:
            ref = _html_escape(item.consultation.paper.reference or item.consultation.paper.name or "")
            paper_ref = f'<br/><span class="reference">Vorlage: {ref}</span>'

        resolution = ""
        if item.resolution_text:
            resolution = (
                '<div class="resolution"><strong>Beschluss:</strong><br/>'
                f'{_html_escape(item.resolution_text)}</div>'
            )

        result = ""
        if item.result:
            result = f'<div class="vote-result">Ergebnis: {_html_escape(item.result)}</div>'

        tops_html += (
            '<div class="agenda-item">'
            f'<span class="number">TOP {number}:</span> {name}{public_marker}'
            f'{paper_ref}{resolution}{result}'
            '</div>'
        )

    html = (
        '<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">'
        f'<title>Protokoll - {_html_escape(meeting_name)}</title>'
        f'{_BASE_STYLES}</head><body>'
        '<div class="header">'
        '<h1>Sitzungsprotokoll</h1>'
        f'<div class="subtitle">{_html_escape(org_name)} - {_html_escape(meeting_name)}</div>'
        '</div>'
        '<table class="meta-table">'
        f'<tr><td>Gremium</td><td>{_html_escape(org_name)}</td></tr>'
        f'<tr><td>Beginn</td><td>{_format_date(meeting.start)}</td></tr>'
        f'<tr><td>Ende</td><td>{_format_date(meeting.end) if meeting.end else "Nicht erfasst"}</td></tr>'
        f'<tr><td>Ort</td><td>{location_str or "Nicht angegeben"}</td></tr>'
        f'<tr><td>Status</td><td>{_html_escape(meeting.meeting_state or "")}</td></tr>'
        '</table>'
    )

    if attendance_html:
        html += attendance_html
    else:
        html += '<h2>Anwesenheit</h2><p style="color: #9ca3af;">Keine Anwesenheitsdaten vorhanden.</p>'

    html += f'<h2>Tagesordnung und Beschluesse ({len(agenda_items)} Punkte)</h2>'

    if tops_html:
        html += tops_html
    else:
        html += '<p style="color: #9ca3af;">Keine Tagesordnungspunkte vorhanden.</p>'

    html += _footer_html()
    html += '</body></html>'
    return html
