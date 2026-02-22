export const dynamic = "force-dynamic";

export async function GET() {
  const backendUrl = process.env.BACKEND_URL || "http://backend:8000";
  try {
    const res = await fetch(`${backendUrl}/api/push/vapid-public-key`);
    return Response.json(await res.json());
  } catch {
    return Response.json({ key: "" }, { status: 503 });
  }
}
