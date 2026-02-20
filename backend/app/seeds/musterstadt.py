"""
Demo-Daten fuer Musterstadt
Generiert realistische Testdaten fuer das aitema|Rats RIS.

Ausfuehren:
    cd backend
    python -m app.seeds.musterstadt

Oder per FastAPI Startup-Hook:
    from app.seeds.musterstadt import seed_musterstadt
    seed_musterstadt(db, tenant_id="musterstadt")
"""
import uuid
import random
from datetime import datetime, date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.oparl import (
    OParlSystem, Body, LegislativeTerm, Organization, Person,
    Membership, Location, Meeting, AgendaItem, Paper, Consultation, File,
)

TENANT_ID = "musterstadt"
NOW = datetime.utcnow()
TODAY = date.today()


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def _id() -> str:
    return str(uuid.uuid4())


def _date_offset(days: int) -> date:
    return TODAY + timedelta(days=days)


def _dt_offset(days: int, hour: int = 17, minute: int = 0) -> datetime:
    d = TODAY + timedelta(days=days)
    return datetime(d.year, d.month, d.day, hour, minute)


def _past_date(months_ago: int) -> date:
    return TODAY - timedelta(days=months_ago * 30)


# ------------------------------------------------------------------ #
# 1. OParl System & Body                                              #
# ------------------------------------------------------------------ #

def _create_system(db: Session) -> OParlSystem:
    system = OParlSystem(
        id=_id(),
        name="aitema|Rats – Musterstadt",
        website="https://musterstadt.de/ratsinformation",
        contact_email="rats@musterstadt.de",
        contact_name="IT-Abteilung Musterstadt",
        vendor="https://aitema.de",
        product="https://github.com/aitema/ratsinformationssystem",
        created=NOW,
        modified=NOW,
    )
    db.add(system)
    return system


def _create_body(db: Session, system: OParlSystem) -> Body:
    body = Body(
        id=_id(),
        tenant_id=TENANT_ID,
        system_id=system.id,
        name="Stadt Musterstadt",
        short_name="Musterstadt",
        body_type="Gemeinde",
        classification="Stadt",
        contact_email="buergerbuero@musterstadt.de",
        contact_name="Buergerbuero Musterstadt",
        ags="09771234",
        rgs="097712340000",
        web="https://musterstadt.de",
        created=NOW,
        modified=NOW,
    )
    db.add(body)
    return body


# ------------------------------------------------------------------ #
# 2. Locations                                                        #
# ------------------------------------------------------------------ #

def _create_locations(db: Session, body: Body) -> dict:
    locs = {}

    entries = [
        ("rathaus",      "Rathaus Musterstadt",    "Rathausplatz 1",   None,                "84001", "Musterstadt"),
        ("grosser_saal", "Grosser Sitzungssaal",   "Rathausplatz 1",   "Sitzungssaal 1.OG", "84001", "Musterstadt"),
        ("kleiner_saal", "Kleiner Sitzungssaal",   "Rathausplatz 1",   "Zimmer 215",        "84001", "Musterstadt"),
        ("feuerwehr",    "Feuerwehrgeraetehaus",   "Hauptstrasse 42",  None,                "84001", "Musterstadt"),
        ("schule",       "Grundschule Musterstadt","Schulweg 5",       None,                "84002", "Musterstadt-Nord"),
        ("stadthalle",   "Stadthalle Musterstadt", "Am Stadtpark 12",  None,                "84001", "Musterstadt"),
    ]

    for key, name, street, room, plz, locality in entries:
        loc = Location(
            id=_id(),
            tenant_id=TENANT_ID,
            body_id=body.id,
            name=name,
            street_address=street,
            room=room,
            postal_code=plz,
            locality=locality,
            created=NOW,
            modified=NOW,
        )
        db.add(loc)
        locs[key] = loc

    return locs


# ------------------------------------------------------------------ #
# 3. Legislative Term                                                 #
# ------------------------------------------------------------------ #

def _create_legislative_term(db: Session, body: Body) -> LegislativeTerm:
    term = LegislativeTerm(
        id=_id(),
        tenant_id=TENANT_ID,
        body_id=body.id,
        name="Wahlperiode 2021 – 2026",
        short_name="WP 2021/26",
        start_date=date(2021, 5, 15),
        end_date=date(2026, 5, 14),
        created=NOW,
        modified=NOW,
    )
    db.add(term)
    return term


# ------------------------------------------------------------------ #
# 4. Organizations (10)                                               #
# ------------------------------------------------------------------ #

def _create_organizations(db: Session, body: Body, locs: dict) -> dict:
    orgs = {}

    defs = [
        # key, name, short_name, org_type, classification
        ("stadtrat",     "Stadtrat Musterstadt",              "Stadtrat",    "ausschuss",  "Hauptgremium"),
        ("hauptaus",     "Hauptausschuss",                    "HA",          "ausschuss",  "Ausschuss"),
        ("bauaus",       "Bau- und Planungsausschuss",         "BPA",         "ausschuss",  "Ausschuss"),
        ("finanzaus",    "Finanz- und Wirtschaftsausschuss",   "FWA",         "ausschuss",  "Ausschuss"),
        ("sozialaus",    "Sozial- und Kulturausschuss",        "SKA",         "ausschuss",  "Ausschuss"),
        ("cdu",          "CDU-Fraktion",                      "CDU",         "fraktion",   "Fraktion"),
        ("spd",          "SPD-Fraktion",                      "SPD",         "fraktion",   "Fraktion"),
        ("gruene",       "Fraktion Buendnis 90/Die Gruenen",  "GRUENE",      "fraktion",   "Fraktion"),
        ("fdp",          "FDP-Fraktion",                      "FDP",         "fraktion",   "Fraktion"),
        ("verwaltung",   "Stadtverwaltung Musterstadt",       "Verwaltung",  "verwaltung", "Verwaltung"),
    ]

    for key, name, short_name, org_type, classification in defs:
        loc_id = locs["rathaus"].id if key == "verwaltung" else locs["grosser_saal"].id
        org = Organization(
            id=_id(),
            tenant_id=TENANT_ID,
            body_id=body.id,
            name=name,
            short_name=short_name,
            organization_type=org_type,
            classification=classification,
            location_id=loc_id,
            start_date=date(2021, 5, 15),
            created=NOW,
            modified=NOW,
        )
        db.add(org)
        orgs[key] = org

    return orgs


# ------------------------------------------------------------------ #
# 5. Persons (35)                                                     #
# ------------------------------------------------------------------ #

PERSON_DATA = [
    # family_name, given_name, form_of_address, gender, fraktion_key, role_stadtrat
    ("Huber",       "Klaus",      "Herr",  "male",   "cdu",     "Buergermeister"),
    ("Maier",       "Sabine",     "Frau",  "female", "cdu",     "Zweite Buergermeisterin"),
    ("Mueller",     "Thomas",     "Herr",  "male",   "cdu",     "Stadtrat"),
    ("Fischer",     "Monika",     "Frau",  "female", "cdu",     "Stadtraetin"),
    ("Schneider",   "Andreas",    "Herr",  "male",   "cdu",     "Stadtrat"),
    ("Zimmermann",  "Elisabeth",  "Frau",  "female", "cdu",     "Stadtraetin"),
    ("Braun",       "Michael",    "Herr",  "male",   "cdu",     "Stadtrat"),
    ("Hartmann",    "Christina",  "Frau",  "female", "cdu",     "Stadtraetin"),
    ("Wagner",      "Peter",      "Herr",  "male",   "spd",     "Stadtrat"),
    ("Becker",      "Petra",      "Frau",  "female", "spd",     "Stadtraetin"),
    ("Hoffmann",    "Frank",      "Herr",  "male",   "spd",     "Stadtrat"),
    ("Koch",        "Ursula",     "Frau",  "female", "spd",     "Stadtraetin"),
    ("Richter",     "Juergen",    "Herr",  "male",   "spd",     "Stadtrat"),
    ("Bauer",       "Angelika",   "Frau",  "female", "spd",     "Stadtraetin"),
    ("Wolf",        "Stefan",     "Herr",  "male",   "spd",     "Stadtrat"),
    ("Schroeder",   "Katrin",     "Frau",  "female", "gruene",  "Stadtraetin"),
    ("Neumann",     "Markus",     "Herr",  "male",   "gruene",  "Stadtrat"),
    ("Lange",       "Julia",      "Frau",  "female", "gruene",  "Stadtraetin"),
    ("Schwarz",     "Daniel",     "Herr",  "male",   "gruene",  "Stadtrat"),
    ("Klein",       "Susanne",    "Frau",  "female", "gruene",  "Stadtraetin"),
    ("Schulz",      "Tobias",     "Herr",  "male",   "gruene",  "Stadtrat"),
    ("Krause",      "Martina",    "Frau",  "female", "fdp",     "Stadtraetin"),
    ("Schmidt",     "Rainer",     "Herr",  "male",   "fdp",     "Stadtrat"),
    ("Werner",      "Heike",      "Frau",  "female", "fdp",     "Stadtraetin"),
    ("Koenig",      "Bernd",      "Herr",  "male",   "fdp",     "Stadtrat"),
    # Verwaltung
    ("Winkler",     "Gerhard",    "Herr",  "male",   "verwaltung", "Stadtkaemmerer"),
    ("Vogel",       "Renate",     "Frau",  "female", "verwaltung", "Stadtbaumeisterin"),
    ("Frank",       "Hans-Peter", "Herr",  "male",   "verwaltung", "Stadtjurist"),
    ("Weber",       "Brigitte",   "Frau",  "female", "verwaltung", "Leitung Sozialamt"),
    ("Kramer",      "Dieter",     "Herr",  "male",   "verwaltung", "Leitung Ordnungsamt"),
    # Weitere Stadtraete
    ("Jung",        "Claudia",    "Frau",  "female", "cdu",     "Stadtraetin"),
    ("Hahn",        "Wolfgang",   "Herr",  "male",   "spd",     "Stadtrat"),
    ("Henning",     "Lena",       "Frau",  "female", "gruene",  "Stadtraetin"),
    ("Keller",      "Georg",      "Herr",  "male",   "fdp",     "Stadtrat"),
    ("Lehmann",     "Irene",      "Frau",  "female", "spd",     "Stadtraetin"),
]


def _create_persons(db: Session, body: Body) -> list:
    persons = []
    for family, given, form, gender, _, _ in PERSON_DATA:
        p = Person(
            id=_id(),
            tenant_id=TENANT_ID,
            body_id=body.id,
            family_name=family,
            given_name=given,
            form_of_address=form,
            gender=gender,
            name=f"{form} {given} {family}",
            email=[f"{given.lower().replace('-', '.')}.{family.lower()}@musterstadt.de"],
            created=NOW,
            modified=NOW,
        )
        db.add(p)
        persons.append(p)
    return persons


# ------------------------------------------------------------------ #
# 6. Memberships (40)                                                 #
# ------------------------------------------------------------------ #

def _create_memberships(
    db: Session,
    persons: list,
    orgs: dict,
) -> list:
    memberships = []

    # Map persons by index to PERSON_DATA
    for i, person in enumerate(persons):
        family, given, form, gender, fraktion_key, role = PERSON_DATA[i]

        # Membership in Fraktion/Verwaltung
        if fraktion_key in orgs:
            is_chair = role in ("Buergermeister", "Zweite Buergermeisterin")
            m = Membership(
                id=_id(),
                tenant_id=TENANT_ID,
                person_id=person.id,
                organization_id=orgs[fraktion_key].id,
                role="Vorsitzende/r" if is_chair else "Mitglied",
                voting_right=True,
                start_date=date(2021, 5, 15),
                created=NOW,
                modified=NOW,
            )
            db.add(m)
            memberships.append(m)

        # Membership im Stadtrat fuer alle Stadtraete (nicht Verwaltung)
        if fraktion_key != "verwaltung":
            is_bgm = role == "Buergermeister"
            m2 = Membership(
                id=_id(),
                tenant_id=TENANT_ID,
                person_id=person.id,
                organization_id=orgs["stadtrat"].id,
                role="Buergermeister" if is_bgm else role,
                voting_right=True,
                start_date=date(2021, 5, 15),
                created=NOW,
                modified=NOW,
            )
            db.add(m2)
            memberships.append(m2)

    # Ausschuss-Besetzung: Hauptausschuss (8 Mitglieder)
    stadtrat_persons = [p for i, p in enumerate(persons) if PERSON_DATA[i][4] != "verwaltung"]
    for idx, p in enumerate(stadtrat_persons[:8]):
        m = Membership(
            id=_id(),
            tenant_id=TENANT_ID,
            person_id=p.id,
            organization_id=orgs["hauptaus"].id,
            role="Vorsitzende/r" if idx == 0 else "Mitglied",
            voting_right=True,
            start_date=date(2021, 5, 15),
            created=NOW,
            modified=NOW,
        )
        db.add(m)
        memberships.append(m)

    # Bau- und Planungsausschuss (7 Mitglieder)
    for idx, p in enumerate(stadtrat_persons[2:9]):
        m = Membership(
            id=_id(),
            tenant_id=TENANT_ID,
            person_id=p.id,
            organization_id=orgs["bauaus"].id,
            role="Vorsitzende/r" if idx == 0 else "Mitglied",
            voting_right=True,
            start_date=date(2021, 5, 15),
            created=NOW,
            modified=NOW,
        )
        db.add(m)
        memberships.append(m)

    # Finanz- und Wirtschaftsausschuss (7 Mitglieder)
    for idx, p in enumerate(stadtrat_persons[5:12]):
        m = Membership(
            id=_id(),
            tenant_id=TENANT_ID,
            person_id=p.id,
            organization_id=orgs["finanzaus"].id,
            role="Vorsitzende/r" if idx == 0 else "Mitglied",
            voting_right=True,
            start_date=date(2021, 5, 15),
            created=NOW,
            modified=NOW,
        )
        db.add(m)
        memberships.append(m)

    # Sozial- und Kulturausschuss (7 Mitglieder)
    for idx, p in enumerate(stadtrat_persons[10:17]):
        m = Membership(
            id=_id(),
            tenant_id=TENANT_ID,
            person_id=p.id,
            organization_id=orgs["sozialaus"].id,
            role="Vorsitzende/r" if idx == 0 else "Mitglied",
            voting_right=True,
            start_date=date(2021, 5, 15),
            created=NOW,
            modified=NOW,
        )
        db.add(m)
        memberships.append(m)

    return memberships


# ------------------------------------------------------------------ #
# 7. Files (Beispiel-Dokumente)                                       #
# ------------------------------------------------------------------ #

def _make_file(
    db: Session,
    name: str,
    file_name: str,
    mime_type: str = "application/pdf",
    size: int = None,
) -> File:
    size = size or random.randint(50_000, 2_500_000)
    f = File(
        id=_id(),
        tenant_id=TENANT_ID,
        name=name,
        file_name=file_name,
        mime_type=mime_type,
        size=size,
        access_url=f"https://musterstadt.de/dokumente/{file_name}",
        download_url=f"https://musterstadt.de/dokumente/{file_name}",
        created=NOW,
        modified=NOW,
    )
    db.add(f)
    return f


# ------------------------------------------------------------------ #
# 8. Papers (80)                                                      #
# ------------------------------------------------------------------ #

PAPER_DEFINITIONS = [
    # reference, name, paper_type, months_ago
    # Bebauungsplaene
    ("2025/BP-001", "Bebauungsplan Nr. 42 'Wohngebiet Nordhang' – Aufstellungsbeschluss", "Beschlussvorlage", 11),
    ("2025/BP-002", "Bebauungsplan Nr. 43 'Gewerbegebiet Sued' – Entwurf", "Beschlussvorlage", 10),
    ("2025/BP-003", "Bebauungsplan Nr. 44 'Schulerweiterung' – Satzungsbeschluss", "Beschlussvorlage", 9),
    ("2025/BP-004", "Aenderung Flaechennutzungsplan: Umwidmung Acker zu Wohnbauland", "Beschlussvorlage", 8),
    ("2025/BP-005", "Vorkaufsrecht nach § 24 BauGB: Grundstueck Hauptstrasse 17", "Beschlussvorlage", 7),
    # Haushalt
    ("2025/HH-001", "Haushaltsplan 2025 – Einbringung", "Beschlussvorlage", 12),
    ("2025/HH-002", "Haushaltsplan 2025 – Verabschiedung", "Beschlussvorlage", 11),
    ("2025/HH-003", "Nachtragshaushaltsplan 2025", "Beschlussvorlage", 6),
    ("2025/HH-004", "Jahresabschluss 2024", "Beschlussvorlage", 5),
    ("2025/HH-005", "Mittelfristige Finanzplanung 2025 – 2029", "Beschlussvorlage", 11),
    ("2025/HH-006", "Gebuehrenordnung Kinderbetreuung – Anpassung 2026", "Beschlussvorlage", 4),
    ("2025/HH-007", "Investitionsprogramm Strassensanierung 2025/2026", "Beschlussvorlage", 7),
    # Schulentwicklung
    ("2025/SCH-001", "Schulentwicklungsplan 2025 – 2030", "Beschlussvorlage", 10),
    ("2025/SCH-002", "Sanierung Grundschule Musterstadt – Kostenuebernahme", "Beschlussvorlage", 8),
    ("2025/SCH-003", "Einrichtung einer Ganztagsschule an der Grundschule Nord", "Beschlussvorlage", 6),
    ("2025/SCH-004", "Digitalpakt Schule: Ausstattung mit Tablets und WLAN", "Beschlussvorlage", 9),
    ("2025/SCH-005", "Schulsozialarbeit – Aufstockung Personalstellen", "Beschlussvorlage", 3),
    # Infrastruktur
    ("2025/INF-001", "Erneuerung Wasserversorgung Ortschaft Kleindorf", "Beschlussvorlage", 10),
    ("2025/INF-002", "Radwegekonzept Musterstadt 2025 – 2030", "Beschlussvorlage", 9),
    ("2025/INF-003", "Sanierung Bruecke Muehlenbach", "Beschlussvorlage", 7),
    ("2025/INF-004", "Breitbandausbau: Foerderantrag Glasfaser", "Beschlussvorlage", 8),
    ("2025/INF-005", "OEPNV-Konzept: Erweiterung Buslinien", "Beschlussvorlage", 5),
    ("2025/INF-006", "Errichtung Ladeinfrastruktur Elektromobilitaet", "Beschlussvorlage", 4),
    ("2025/INF-007", "Sanierung Hallenbad Musterstadt", "Beschlussvorlage", 11),
    # Umwelt & Klimaschutz
    ("2025/UMW-001", "Klimaschutzkonzept Musterstadt 2035", "Beschlussvorlage", 10),
    ("2025/UMW-002", "Aufstellung Klimaschutzzwischenbericht 2025", "Mitteilung", 6),
    ("2025/UMW-003", "Solarpflicht kommunale Gebaeude", "Beschlussvorlage", 7),
    ("2025/UMW-004", "Anlage Stadtgarten am Muehlenbach", "Beschlussvorlage", 4),
    ("2025/UMW-005", "Foerderung privater Photovoltaikanlagen", "Beschlussvorlage", 8),
    # Soziales & Kultur
    ("2025/SOZ-001", "Kitabedarfsplan 2025/2026", "Beschlussvorlage", 9),
    ("2025/SOZ-002", "Erweiterung Kita Sonnenschein – Baugenehmigung", "Beschlussvorlage", 7),
    ("2025/SOZ-003", "Senioren-Fahrdienst: Verlaengerung Foerderung", "Beschlussvorlage", 5),
    ("2025/SOZ-004", "Konzept Integration und Teilhabe 2025", "Beschlussvorlage", 8),
    ("2025/SOZ-005", "Stadtbibliothek: Digitale Ausstattung", "Beschlussvorlage", 6),
    ("2025/SOZ-006", "Jugendeinrichtung Stadtmitte – Sanierung", "Beschlussvorlage", 3),
    ("2025/SOZ-007", "Foerderrichtlinie Vereinsfoerderung – Neufassung", "Beschlussvorlage", 11),
    # Antraege Fraktionen
    ("2025/ANT-001", "Antrag SPD: Einrichtung eines Fahrradverleihsystems", "Antrag", 8),
    ("2025/ANT-002", "Antrag GRUENE: Ausweitung Gruenflaechen Innenstadt", "Antrag", 7),
    ("2025/ANT-003", "Antrag FDP: Vereinfachung Baugenehmigungsverfahren", "Antrag", 6),
    ("2025/ANT-004", "Antrag CDU: Erweiterung Parkplaetze Bahnhof", "Antrag", 9),
    ("2025/ANT-005", "Antrag SPD: Kostenloser Nahverkehr fuer Senioren", "Antrag", 5),
    ("2025/ANT-006", "Antrag GRUENE: Pestizidfreie Gruenanlagen", "Antrag", 4),
    ("2025/ANT-007", "Antrag FDP: Errichtung Coworking-Space Innenstadt", "Antrag", 3),
    ("2025/ANT-008", "Antrag CDU: Marktsonntage Innenstadt", "Antrag", 10),
    # Anfragen
    ("2025/ANF-001", "Anfrage SPD: Sachstand Radwegeplanung Ortschaft Felddorf", "Anfrage", 8),
    ("2025/ANF-002", "Anfrage GRUENE: Luftqualitaet Hauptstrasse – Messergebnisse", "Anfrage", 7),
    ("2025/ANF-003", "Anfrage FDP: Kosten Rathaus-Sanierung", "Anfrage", 6),
    ("2025/ANF-004", "Anfrage CDU: Belegungsstatistik Kinderbetreuung", "Anfrage", 5),
    ("2025/ANF-005", "Anfrage SPD: Zustand kommunaler Spielplaetze", "Anfrage", 4),
    # Mitteilungen
    ("2025/MIT-001", "Sachstandsbericht Stadtentwicklung Q1/2025", "Mitteilung", 9),
    ("2025/MIT-002", "Bericht Buergermeister: Wirtschaftsfoerderung 2024", "Mitteilung", 8),
    ("2025/MIT-003", "Jahresbericht Stadtwerke 2024", "Mitteilung", 7),
    ("2025/MIT-004", "Sachstandsbericht Wohnungsbau 2025", "Mitteilung", 6),
    ("2025/MIT-005", "Quartalsbericht Finanzen Q2/2025", "Mitteilung", 5),
    ("2025/MIT-006", "Bericht Integrationsbeirat 2025", "Mitteilung", 4),
    ("2025/MIT-007", "Sachstandsbericht Klimaschutz Q3/2025", "Mitteilung", 3),
    ("2025/MIT-008", "Jahresbericht Stadtbuecherei 2024", "Mitteilung", 10),
    # Aktuell / zukuenftig
    ("2026/BP-001", "Bebauungsplan Nr. 45 'Wohngebiet Suedwest' – Vorbereitende Untersuchungen", "Beschlussvorlage", -1),
    ("2026/HH-001", "Aufstellung Haushaltsplan 2026 – Eckwertebeschluss", "Beschlussvorlage", -2),
    ("2026/INF-001", "Strassensanierung Bahnhofstrasse – Vergabe", "Beschlussvorlage", -1),
    ("2026/SOZ-001", "Kitaneubau Weststadt – Grundsatzbeschluss", "Beschlussvorlage", -3),
    ("2026/UMW-001", "Foerderantrag Bundesfoerderprogramm Klimaschutz", "Beschlussvorlage", -2),
    ("2026/ANT-001", "Antrag SPD: Haushaltsbegleitantrag Soziales 2026", "Antrag", -1),
    ("2026/ANT-002", "Antrag GRUENE: Klimaneutralitaet 2040", "Antrag", -2),
    ("2026/MIT-001", "Sachstandsbericht Stadtentwicklung Q4/2025", "Mitteilung", -1),
    # Vergangenheit tiefere Vergangenheit
    ("2024/HH-001", "Haushaltsplan 2024 – Verabschiedung", "Beschlussvorlage", 14),
    ("2024/BP-001", "Bebauungsplan Nr. 40 'Gewerbegebiet Nord' – Satzungsbeschluss", "Beschlussvorlage", 18),
    ("2024/INF-001", "Sanierung Ortsdurchfahrt Kleindorf – Kostenfeststellung", "Beschlussvorlage", 15),
    ("2024/SCH-001", "Schulentwicklungsplan 2024 – Zwischenbilanz", "Mitteilung", 16),
    ("2024/SOZ-001", "Bericht Fluechtlingsunterkunft: Sachstandsbericht", "Mitteilung", 17),
    ("2024/ANT-001", "Antrag CDU: Erweiterung Freizeitzentrum", "Antrag", 15),
    ("2024/ANT-002", "Antrag SPD: Grundsteuerreform – Auswirkungen", "Antrag", 14),
    ("2024/ANF-001", "Anfrage GRUENE: Sachstand Solaranlage Rathaus", "Anfrage", 16),
    ("2023/HH-001", "Haushaltsplan 2023 – Verabschiedung", "Beschlussvorlage", 26),
    ("2023/BP-001", "Bebauungsplan Nr. 38 'Wohngebiet Am Park' – Satzungsbeschluss", "Beschlussvorlage", 28),
    ("2023/INF-001", "Breitbandausbau Phase 1 – Abschluss", "Mitteilung", 30),
    ("2023/SOZ-001", "Kita-Bedarfsplanung 2023 – Massnahmen", "Beschlussvorlage", 27),
]


def _create_papers(db: Session, body: Body, orgs: dict, persons: list) -> list:
    papers = []
    fraktionen = [orgs["cdu"], orgs["spd"], orgs["gruene"], orgs["fdp"]]

    for ref, name, paper_type, months_ago in PAPER_DEFINITIONS:
        paper_date = _past_date(months_ago) if months_ago > 0 else _date_offset(abs(months_ago) * 7)

        # Hauptdatei
        slug = ref.replace("/", "_").replace(" ", "_")
        main_file = _make_file(
            db,
            name=f"{name} – Vorlage",
            file_name=f"{slug}_vorlage.pdf",
        )

        paper = Paper(
            id=_id(),
            tenant_id=TENANT_ID,
            body_id=body.id,
            name=name,
            reference=ref,
            date=paper_date,
            paper_type=paper_type,
            main_file_id=main_file.id,
            created=NOW,
            modified=NOW,
        )
        db.add(paper)
        db.flush()

        # Originator
        if paper_type in ("Antrag", "Anfrage"):
            if "SPD" in name:
                paper.originator_organizations.append(orgs["spd"])
            elif "GRUENE" in name or "Grüne" in name:
                paper.originator_organizations.append(orgs["gruene"])
            elif "FDP" in name:
                paper.originator_organizations.append(orgs["fdp"])
            else:
                paper.originator_organizations.append(orgs["cdu"])
        else:
            paper.originator_organizations.append(orgs["verwaltung"])

        papers.append(paper)

    return papers


# ------------------------------------------------------------------ #
# 9. Meetings (40) mit AgendaItems & Consultations                   #
# ------------------------------------------------------------------ #

def _create_meetings(
    db: Session,
    body: Body,
    orgs: dict,
    locs: dict,
    papers: list,
) -> list:
    meetings = []
    paper_iter = iter(papers)

    def _next_paper():
        try:
            return next(paper_iter)
        except StopIteration:
            return None

    # 12 Monate Stadtrat-Sitzungen (monatlich)
    stadtrat_meetings = [
        ("Stadtrat – Sitzung", "stadtrat", "grosser_saal", months_ago, "completed")
        for months_ago in range(12, 0, -1)
    ]
    # 3 zukuenftige
    stadtrat_meetings += [
        ("Stadtrat – Sitzung", "stadtrat", "grosser_saal", -offset, "scheduled")
        for offset in [30, 60, 90]
    ]

    # Ausschuss-Sitzungen (je 5)
    ausschuss_meetings = []
    for org_key, loc_key in [
        ("hauptaus", "kleiner_saal"),
        ("bauaus", "kleiner_saal"),
        ("finanzaus", "kleiner_saal"),
        ("sozialaus", "kleiner_saal"),
    ]:
        for mo in [9, 6, 3, -14, -44]:
            state = "completed" if mo > 0 else "scheduled"
            ausschuss_meetings.append(
                (f"{orgs[org_key].name} – Sitzung", org_key, loc_key, mo, state)
            )

    all_meeting_defs = stadtrat_meetings + ausschuss_meetings

    for m_idx, (m_name, org_key, loc_key, offset, state) in enumerate(all_meeting_defs):
        if offset > 0:
            # Vergangenheit
            m_dt = _dt_offset(-offset * 30, hour=17)
        else:
            # Zukunft
            m_dt = _dt_offset(abs(offset), hour=17)

        m_end = datetime(m_dt.year, m_dt.month, m_dt.day, 19, 30)

        org = orgs[org_key]
        loc = locs[loc_key]

        invitation = _make_file(
            db,
            name=f"Einladung {m_name} {m_dt.strftime('%d.%m.%Y')}",
            file_name=f"einladung_{org_key}_{m_dt.strftime('%Y%m%d')}.pdf",
        )

        meeting = Meeting(
            id=_id(),
            tenant_id=TENANT_ID,
            body_id=body.id,
            name=f"{m_name} {m_dt.strftime('%d.%m.%Y')}",
            meeting_state=state,
            cancelled=False,
            start=m_dt,
            end=m_end,
            location_id=loc.id,
            organization_id=org.id,
            invitation_id=invitation.id,
            created=NOW,
            modified=NOW,
        )

        if state == "completed":
            protocol = _make_file(
                db,
                name=f"Sitzungsprotokoll {m_dt.strftime('%d.%m.%Y')}",
                file_name=f"protokoll_{org_key}_{m_dt.strftime('%Y%m%d')}.pdf",
            )
            meeting.results_protocol_id = protocol.id

        db.add(meeting)
        db.flush()

        # Tagesordnungspunkte
        agenda_tops = [
            ("1", "Genehmigung der Tagesordnung", True, None),
            ("2", "Genehmigung des Protokolls der letzten Sitzung", True, None),
        ]

        # Fachliche TOPs mit Vorlagen
        for top_num in range(3, 7):
            paper = _next_paper()
            if paper:
                agenda_tops.append(
                    (str(top_num), paper.name, True, paper)
                )
            else:
                agenda_tops.append(
                    (str(top_num), f"Verschiedenes / Bericht der Verwaltung", True, None)
                )

        agenda_tops.append(
            (str(len(agenda_tops) + 1), "Bekanntgaben und Verschiedenes", True, None)
        )

        # Nichtoeffentlicher TOP
        agenda_tops.append(
            (str(len(agenda_tops) + 1), "Personalangelegenheiten (nicht oeffentlich)", False, None)
        )

        for order, (number, top_name, public, paper) in enumerate(agenda_tops):
            ai = AgendaItem(
                id=_id(),
                tenant_id=TENANT_ID,
                meeting_id=meeting.id,
                number=number,
                order=order,
                name=top_name,
                public=public,
                result="Einstimmig beschlossen." if state == "completed" and public and paper else None,
                created=NOW,
                modified=NOW,
            )
            db.add(ai)
            db.flush()

            if paper and public:
                consultation = Consultation(
                    id=_id(),
                    tenant_id=TENANT_ID,
                    paper_id=paper.id,
                    agenda_item_id=ai.id,
                    organization_id=org.id,
                    authoritative=(org_key == "stadtrat"),
                    role="Beschlussfassung" if org_key == "stadtrat" else "Vorberatung",
                    created=NOW,
                    modified=NOW,
                )
                db.add(consultation)

        meetings.append(meeting)

    return meetings


# ------------------------------------------------------------------ #
# Main seed function                                                  #
# ------------------------------------------------------------------ #

def seed_musterstadt(db: Session, tenant_id: str = TENANT_ID) -> dict:
    """
    Fuellt die Datenbank mit Demo-Daten fuer Musterstadt.
    Gibt ein Dict mit allen erstellten Objekten zurueck.
    """
    print(f"Seeding Musterstadt (tenant_id={tenant_id})...")

    system = _create_system(db)
    db.flush()
    print(f"  System: {system.name}")

    body = _create_body(db, system)
    db.flush()
    print(f"  Body: {body.name}")

    locs = _create_locations(db, body)
    db.flush()
    print(f"  Locations: {len(locs)}")

    term = _create_legislative_term(db, body)
    db.flush()
    print(f"  LegislativeTerm: {term.name}")

    orgs = _create_organizations(db, body, locs)
    db.flush()
    print(f"  Organizations: {len(orgs)}")

    persons = _create_persons(db, body)
    db.flush()
    print(f"  Persons: {len(persons)}")

    memberships = _create_memberships(db, persons, orgs)
    db.flush()
    print(f"  Memberships: {len(memberships)}")

    papers = _create_papers(db, body, orgs, persons)
    db.flush()
    print(f"  Papers: {len(papers)}")

    meetings = _create_meetings(db, body, orgs, locs, papers)
    db.commit()
    print(f"  Meetings: {len(meetings)}")
    print("Seeding abgeschlossen.")

    return {
        "system": system,
        "body": body,
        "locations": locs,
        "term": term,
        "organizations": orgs,
        "persons": persons,
        "memberships": memberships,
        "papers": papers,
        "meetings": meetings,
    }


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_musterstadt(db)
    finally:
        db.close()
