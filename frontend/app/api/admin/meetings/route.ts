// Admin Meetings API Proxy - proxies to OParl endpoint
const BACKEND = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const page = searchParams.get('page') || '1';
  const perPage = searchParams.get('per_page') || '20';

  try {
    // Use OParl body endpoint - body_id needed, use first body or 'default'
    // Try listing meetings via OParl search endpoint
    const res = await fetch(
      `${BACKEND}/api/v1/oparl/search?type=meeting&page=${page}&per_page=${perPage}`,
      { cache: 'no-store' }
    );
    if (res.ok) {
      const data = await res.json();
      return Response.json(data, { status: 200 });
    }
    // Fallback: empty response
    return Response.json({ data: [], pagination: { totalElements: 0, currentPage: 1, totalPages: 0 } });
  } catch (err) {
    return Response.json({ error: 'Backend nicht erreichbar', detail: String(err) }, { status: 503 });
  }
}
