import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const res = await fetch(`${BACKEND_URL}/api/v1/subscriptions/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await res.json().catch(() => ({}));
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error('[subscriptions proxy] error:', err);
    return NextResponse.json(
      { detail: 'Interner Fehler. Bitte versuchen Sie es spaeter erneut.' },
      { status: 502 }
    );
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const email = searchParams.get('email');
  if (!email) {
    return NextResponse.json({ detail: 'email Parameter erforderlich.' }, { status: 400 });
  }
  try {
    const res = await fetch(
      `${BACKEND_URL}/api/v1/subscriptions/?email=${encodeURIComponent(email)}`,
    );
    const data = await res.json().catch(() => ({}));
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json({ detail: 'Fehler beim Laden.' }, { status: 502 });
  }
}
