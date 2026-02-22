import { NextRequest } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const backendUrl = process.env.BACKEND_URL || "http://backend:8000";

  const res = await fetch(`${backendUrl}/api/rag/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    return new Response(
      JSON.stringify({ error: "Backend error", status: res.status }),
      { status: res.status, headers: { "Content-Type": "application/json" } }
    );
  }

  return new Response(res.body, {
    status: 200,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "X-Accel-Buffering": "no",
    },
  });
}
