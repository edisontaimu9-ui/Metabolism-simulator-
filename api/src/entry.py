import json

from workers import Response, WorkerEntrypoint

from api_core import handle

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method == "OPTIONS":
            return Response("", status=204, headers=CORS)
        path = "/" + request.url.split("/", 3)[-1].split("?")[0].strip("/")
        body = None
        if request.method == "POST":
            try:
                body = json.loads(await request.text())
            except ValueError:
                return Response.json({"error": "invalid JSON"}, status=400, headers=CORS)
        status, payload = handle(request.method, path.rstrip("/") or "/", body)
        return Response.json(payload, status=status, headers=CORS)
