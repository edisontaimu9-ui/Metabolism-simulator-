import hmac
import json

from workers import Response, WorkerEntrypoint

from api_core import handle

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-API-Key",
}

PUBLIC = {("GET", "/")}  # health check stays open


def authorized(request, secret) -> bool:
    """Fail closed: no secret configured means nobody gets in."""
    if not secret:
        return False
    supplied = request.headers.get("X-API-Key") or ""
    return hmac.compare_digest(supplied.encode(), str(secret).encode())


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method == "OPTIONS":
            return Response("", status=204, headers=CORS)
        path = "/" + request.url.split("/", 3)[-1].split("?")[0].strip("/")
        path = path.rstrip("/") or "/"
        if (request.method, path) not in PUBLIC and not authorized(
            request, getattr(self.env, "API_KEY", None)
        ):
            return Response.json({"error": "unauthorized"}, status=401, headers=CORS)
        body = None
        if request.method == "POST":
            try:
                body = json.loads(await request.text())
            except ValueError:
                return Response.json({"error": "invalid JSON"}, status=400, headers=CORS)
        status, payload = handle(request.method, path, body)
        return Response.json(payload, status=status, headers=CORS)
