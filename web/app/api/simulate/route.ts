// Server-side proxy: the API key never reaches the browser.
export async function POST(req: Request) {
  const base = process.env.METABOSIM_URL;
  const key = process.env.API_KEY;
  if (!base || !key) return Response.json({ error: "server not configured" }, { status: 500 });

  let body: unknown;
  try { body = await req.json(); } catch { return Response.json({ error: "invalid JSON" }, { status: 400 }); }

  const upstream = await fetch(`${base}/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-API-Key": key },
    body: JSON.stringify(body),
  });
  return new Response(await upstream.text(), {
    status: upstream.status,
    headers: { "Content-Type": "application/json" },
  });
}
