from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from ..opa.client import opa_client
from starlette.responses import Response
from ..keycloak.client import keycloak_service
from ..utils.index import geo_lookup_ip
import httpx
import random


class AuthenticateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.headers.get("X-Forwarded-For", "unknown")
        geo = await geo_lookup_ip(ip)  # type: ignore

        access_token = request.cookies.get("access_token")
        if not access_token:
            auth_header = request.headers.get("authorization") 
            if auth_header and auth_header.startswith("Bearer "):
                access_token = auth_header.split(" ")[1]
        decode_token = {}

        try:
            decode_token = keycloak_service.decode_token(access_token)

        except Exception as e:
            pass

        request.state.user = {
            "username": decode_token.get("preferred_username", "unknown"),
            "email": decode_token.get("email", "unknown"),
            "roles": decode_token.get("realm_access", {}).get("roles", []),
            "auth_time": decode_token.get("auth_time", decode_token.get("iat", 0)),
            "ip": ip,
            "device": request.headers.get("user-agent", "unknown"),
            "country": geo.get("country", "unknown"),
            "city": geo.get("city", "unknown"),
            "isp": geo.get("isp", "unknown"),
            "zip": geo.get("zip", "unknown"),
        }
        response = await call_next(request)
        return response
