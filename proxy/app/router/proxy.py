import httpx
from fastapi import APIRouter, Request, Response, Body
from ..common.config import config


router = APIRouter()

HOP_BY_HOP = {
    "host",
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}



@router.api_route(
    "{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)
async def proxy(path: str, request: Request):
    upstream_url = f"{config.UPSTREAM_URL}/{path}"
    if request.url.query:
        upstream_url += "?" + request.url.query

    headers = {k: v for k, v in request.headers.items() if k.lower() not in HOP_BY_HOP}

    async with httpx.AsyncClient(follow_redirects=False) as client:
        response = await client.request(
            method=request.method,
            url=upstream_url,
            headers=headers,
            content=await request.body(),
            cookies=request.cookies,
        )
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers={
            k: v for k, v in response.headers.items() if k.lower() not in HOP_BY_HOP
        },
        media_type=response.headers.get("content-type"),
    )
