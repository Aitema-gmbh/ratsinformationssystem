import { NextRequest, NextResponse } from 'next/server';

export async function POST(
  _request: NextRequest,
  { params }: { params: { id: string } },
) {
  const backendUrl =
    process.env.BACKEND_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    'http://localhost:8000';
  try {
    const res = await fetch(
      `${backendUrl}/api/export/paper/${params.id}/simple-language`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      },
    );
    if (!res.ok) {
      return NextResponse.json(
        { error: 'Backend-Fehler bei der Generierung' },
        { status: res.status },
      );
    }
    const data = await res.json();
    return NextResponse.json(data);
  } catch (err) {
    console.error('simple-language route error:', err);
    return NextResponse.json({ error: 'Interner Fehler' }, { status: 500 });
  }
}
