import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// -----------------------------------------------------------------------
// Mock-Daten fuer Demo / Fallback wenn Backend-Endpunkt nicht existiert
// -----------------------------------------------------------------------
function generateMockVoting(meetingId: string) {
  return {
    meeting_id: meetingId,
    voting_results: [
      {
        agenda_item_id: 'top-1',
        agenda_item_title: 'Haushaltssatzung 2026 – Erste Lesung',
        yes_votes: 23,
        no_votes: 7,
        abstentions: 3,
        result: 'approved' as const,
        is_public: true,
        individual_votes: [
          { member_name: 'Maria Musterfrau', vote: 'yes' as const, faction: 'SPD' },
          { member_name: 'Hans Beispiel', vote: 'yes' as const, faction: 'CDU' },
          { member_name: 'Petra Schmidt', vote: 'no' as const, faction: 'AfD' },
          { member_name: 'Klaus Werner', vote: 'yes' as const, faction: 'Grüne' },
          { member_name: 'Anna Müller', vote: 'abstain' as const, faction: 'FDP' },
          { member_name: 'Thomas Bauer', vote: 'yes' as const, faction: 'SPD' },
          { member_name: 'Julia Hoffmann', vote: 'no' as const, faction: 'AfD' },
          { member_name: 'Stefan Koch', vote: 'yes' as const, faction: 'CDU' },
        ],
      },
      {
        agenda_item_id: 'top-2',
        agenda_item_title: 'Bebauungsplan Nr. 42 – Gewerbegebiet Nord',
        yes_votes: 18,
        no_votes: 14,
        abstentions: 1,
        result: 'approved' as const,
        is_public: true,
        individual_votes: [
          { member_name: 'Maria Musterfrau', vote: 'yes' as const, faction: 'SPD' },
          { member_name: 'Hans Beispiel', vote: 'no' as const, faction: 'CDU' },
          { member_name: 'Petra Schmidt', vote: 'no' as const, faction: 'AfD' },
          { member_name: 'Klaus Werner', vote: 'no' as const, faction: 'Grüne' },
          { member_name: 'Anna Müller', vote: 'abstain' as const, faction: 'FDP' },
          { member_name: 'Thomas Bauer', vote: 'yes' as const, faction: 'SPD' },
          { member_name: 'Julia Hoffmann', vote: 'no' as const, faction: 'AfD' },
          { member_name: 'Stefan Koch', vote: 'yes' as const, faction: 'CDU' },
        ],
      },
      {
        agenda_item_id: 'top-3',
        agenda_item_title: 'Antrag: Errichtung einer Skateanlage im Stadtpark',
        yes_votes: 12,
        no_votes: 19,
        abstentions: 2,
        result: 'rejected' as const,
        is_public: true,
        individual_votes: [
          { member_name: 'Maria Musterfrau', vote: 'yes' as const, faction: 'SPD' },
          { member_name: 'Hans Beispiel', vote: 'no' as const, faction: 'CDU' },
          { member_name: 'Petra Schmidt', vote: 'no' as const, faction: 'AfD' },
          { member_name: 'Klaus Werner', vote: 'yes' as const, faction: 'Grüne' },
          { member_name: 'Anna Müller', vote: 'abstain' as const, faction: 'FDP' },
          { member_name: 'Thomas Bauer', vote: 'no' as const, faction: 'SPD' },
          { member_name: 'Julia Hoffmann', vote: 'no' as const, faction: 'AfD' },
          { member_name: 'Stefan Koch', vote: 'no' as const, faction: 'CDU' },
        ],
      },
      {
        agenda_item_id: 'top-4',
        agenda_item_title: 'Konzept Klimaschutz 2030 – Weiteres Vorgehen',
        yes_votes: 0,
        no_votes: 0,
        abstentions: 0,
        result: 'deferred' as const,
        is_public: false,
        individual_votes: [],
      },
    ],
  };
}

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  const meetingId = params.id;

  // Versuche zuerst den echten Backend-Endpunkt
  try {
    const backendUrl = `${BACKEND_URL}/api/v1/workflow/meetings/${meetingId}/voting`;
    const res = await fetch(backendUrl, {
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(3000),
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch {
    // Backend nicht erreichbar oder Endpunkt fehlt → Mock-Daten
  }

  // Fallback: realistische Mock-Daten
  return NextResponse.json(generateMockVoting(meetingId));
}
