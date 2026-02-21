// R1: KI-Kurzfassung API Route - proxies to FastAPI backend
export const dynamic = 'force-dynamic';

export async function POST(
  _request: Request,
  { params }: { params: { id: string } }
) {
  const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    const res = await fetch(`${backendUrl}/export/paper/${params.id}/summarize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!res.ok) {
      return Response.json(
        { error: 'KI-Zusammenfassung fehlgeschlagen' },
        { status: res.status }
      );
    }

    const data = await res.json();
    return Response.json(data);
  } catch {
    return Response.json({ error: 'Backend nicht erreichbar' }, { status: 503 });
  }
}
