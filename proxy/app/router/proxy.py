import httpx
from fastapi import APIRouter, Request, Response, Body, HTTPException
from ..common.config import config  
import logging
from typing import List, Dict, Tuple


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

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


SERVICE_MAP = {
    "public": {
        "Target": "http://upstream_public:81",
        "Prefixes": ["/", "/index.php", "/about.php", "/contact.php"]  
    },
    "private": {
        "Target": "http://upstream_private:81",
        "Prefixes": ["/dashboard.php", "/accounts.php", "/transfer.php", 
                     "/transactions.php", "/api.php"]  
    },
    "admin": {
        "Target": "http://upstream_admin:81",
        "Prefixes": ["/admin"]  
    },
    "server": {
        "Target": "http://upstream_server:81",
        "Prefixes": ["/data.php"]  
    }
}


prefix_map_list: List[Tuple[str, str]] = []
for service_name, config in SERVICE_MAP.items():
    target = config["Target"]
    for prefix in config["Prefixes"]:
        prefix_map_list.append((prefix, target))


SORTED_PREFIX_MAP = sorted(prefix_map_list, key=lambda item: len(item[0]), reverse=True)

log.info(f"Proxy Caching {len(SORTED_PREFIX_MAP)} prefixes for {SERVICE_MAP.keys()} services")


@router.api_route(
    "{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)
async def proxy(path: str, request: Request):
    

    request_path = request.url.path
    
    target_upstream_url = None


    for prefix, target in SORTED_PREFIX_MAP:
        if request_path.startswith(prefix):
            target_upstream_url = target
            log.info(f"Path '{request_path}' matched prefix '{prefix}' -> Target '{target}'")
            break  


    if not target_upstream_url:
        log.warning(f"No upstream configured for path: {request_path}")
        raise HTTPException(status_code=404, detail=f"Service for path '{request_path}' not found")

    upstream_url = f"{target_upstream_url}{request_path}"


    if request.url.query:
        upstream_url += "?" + request.url.query

    headers = {k: v for k, v in request.headers.items() if k.lower() not in HOP_BY_HOP}

    log.info(f"Proxying: {request.method} {request.url.path} -> {upstream_url}")

    async with httpx.AsyncClient(follow_redirects=False) as client:
        try:
            response = await client.request(
                method=request.method,
                url=upstream_url,
                headers=headers,
                content=await request.body(),
                cookies=request.cookies,
            )
        except httpx.ConnectError as e:
            log.error(f"Connection error to {upstream_url}: {e}")
            raise HTTPException(status_code=502, detail=f"Bad Gateway: Cannot connect to upstream")

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers={
            k: v for k, v in response.headers.items() if k.lower() not in HOP_BY_HOP
        },
        media_type=response.headers.get("content-type"),
    )