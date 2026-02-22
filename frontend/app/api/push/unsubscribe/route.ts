export const dynamic = "force-dynamic";

export async function DELETE(req: Request) {
  const { searchParams } = new URL(req.url);
  const endpoint = searchParams.get("endpoint") || "";
  const backendUrl = process.env.BACKEND_URL || "http://backend:8000";
  const res = await fetch(
    `${backendUrl}/api/push/unsubscribe?endpoint=${encodeURIComponent(endpoint)}`,
    { method: "DELETE" }
  );
  return Response.json(await res.json());
}
