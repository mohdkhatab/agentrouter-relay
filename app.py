"""AgentRouter relay — deploy on Render.

Forwards /v1/* to https://agentrouter.org with a coding-client
User-Agent (AgentRouter rejects plain clients). The caller's own
AgentRouter API key is passed through in the Authorization header;
no key is stored on the server.
"""
import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

UPSTREAM = os.environ.get("UPSTREAM_BASE", "https://agentrouter.org")
UA = "opencode/1.0.0"
TIMEOUT = httpx.Timeout(300.0, connect=30.0)

app = FastAPI(title="AgentRouter Relay")


@app.get("/")
def root():
    return {"ok": True, "service": "agentrouter-relay", "upstream": UPSTREAM}


@app.get("/health")
def health():
    return {"ok": True}


@app.api_route(
    "/v1/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy(path: str, request: Request):
    url = f"{UPSTREAM}/v1/{path}"
    if request.url.query:
        url += f"?{request.url.query}"
    body = await request.body()
    headers = {"User-Agent": UA, "Content-Type": "application/json", "Accept-Encoding": "identity"}
    auth = request.headers.get("authorization")
    if auth:
        headers["Authorization"] = auth

    client = httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True)
    try:
        upstream_req = client.build_request(
            request.method, url, headers=headers, content=body
        )
        upstream_resp = await client.send(upstream_req, stream=True)
    except httpx.HTTPError as exc:
        await client.aclose()
        return JSONResponse(
            {"error": f"relay upstream failed: {type(exc).__name__}"},
            status_code=502,
        )

    async def stream():
        try:
            async for chunk in upstream_resp.aiter_bytes():
                yield chunk
        finally:
            await upstream_resp.aclose()
            await client.aclose()

    return StreamingResponse(
        stream(),
        status_code=upstream_resp.status_code,
        media_type=upstream_resp.headers.get("content-type", "application/json"),
    )
