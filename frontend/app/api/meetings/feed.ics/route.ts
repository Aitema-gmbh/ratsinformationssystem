// R2: iCal Feed Route - proxies to FastAPI backend
export const dynamic = 'force-dynamic';

export async function GET() {
  const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    const res = await fetch(`${backendUrl}/export/meetings/feed.ics`);

    if (!res.ok) {
      return new Response('iCal feed nicht verfuegbar', { status: 502 });
    }

    const ical = await res.text();
    return new Response(ical, {
      headers: {
        'Content-Type': 'text/calendar; charset=utf-8',
        'Cache-Control': 'public, max-age=3600',
      },
    });
  } catch {
    return new Response('iCal feed nicht erreichbar', { status: 503 });
  }
}
