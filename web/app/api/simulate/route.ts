import { getCloudflareContext } from "@opennextjs/cloudflare";

// Server-side proxy: the API key never reaches the browser.
function setting(name: string): string | undefined {
  try {
    const env = getCloudflareContext().env as unknown as Record<string, string | undefined>;
    if (env?.[name]) return env[name];
  } catch {
    /* not running on Cloudflare (local dev) */
  }
  return process.env[name];
}

export async function POST(req: Request) {
  const base = setting("METABOSIM_URL");
  const key = setting("API_KEY");
  const missing = [!base && "METABOSIM_URL", !key && "API_KEY"].filter(Boolean);
  if (missing.length) {
    return Response.json({ error: `server not configured: missing ${missing.join(", ")}` }, { status: 500 });
  }

  let body: unknown;
  try { body = await req.json(); } catch { return Response.json({ error: "invalid JSON" }, { status: 400 }); }

  const upstream = await fetch(`${base}/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-API-Key": key as string },
    body: JSON.stringify(body),
  });
  return new Response(await upstream.text(), {
    status: upstream.status,
    headers: { "Content-Type": "application/json" },
  });
}
