/**
 * Next.js API Route: POST /api/search/semantic
 * Proxy to FastAPI backend semantic search endpoint.
 */
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('query') || '';
    const limit = parseInt(searchParams.get('limit') || '10', 10);
    const minSimilarity = parseFloat(searchParams.get('min_similarity') || '0.5');

    if (!query || query.trim().length < 2) {
      return NextResponse.json({
        results: [],
        mode: 'semantic',
        query,
        total: 0,
        message: 'Suchbegriff zu kurz',
      });
    }

    const backendUrl = `${BACKEND_URL}/api/v1/search/semantic`;

    const res = await fetch(backendUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query.trim(),
        limit,
        min_similarity: minSimilarity,
      }),
      signal: AbortSignal.timeout(30_000),
    });

    if (!res.ok) {
      console.error(`[semantic-search] Backend error: ${res.status}`);
      return NextResponse.json(
        { error: 'Backend-Fehler', status: res.status },
        { status: res.status },
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('[semantic-search] Error:', error);
    return NextResponse.json({
      results: [],
      mode: 'semantic_error',
      query: '',
      total: 0,
      message: 'Semantische Suche vorübergehend nicht verfügbar',
    });
  }
}

export async function GET(request: NextRequest) {
  return POST(request);
}
