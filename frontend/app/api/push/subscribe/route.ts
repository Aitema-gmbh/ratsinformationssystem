export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const body = await req.json();
  const backendUrl = process.env.BACKEND_URL || "http://backend:8000";
  const res = await fetch(`${backendUrl}/api/push/subscribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return Response.json(await res.json());
}
