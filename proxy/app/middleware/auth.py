from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from ..opa.client import opa_client
from starlette.responses import Response
from ..keycloak.client import keycloak_service

PUBLIC_EXACT = {"/docs", "/openapi.json", "/docs/oauth2-redirect", "/healthz", "/token"}
PUBLIC_PREFIXES = (
    "/static/",
    "/public/",
)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in PUBLIC_EXACT or path.startswith(PUBLIC_PREFIXES):
            return await call_next(request)

        token_header = request.headers.get("Authorization")

        if token_header:
            access_token = token_header.split(" ")[1]  # Bearer <token>
            try:
                decode_token = keycloak_service.decode_token(access_token)
            except Exception as e:
                # return detailed error message
                return Response(content=f"{e}", status_code=401)
        else:
            return Response(content="Dont have token", status_code=401)

        print(decode_token)

        input_data = {
            "method": request.method,
            "path": path.split("/")[1:] if path else [],
            "roles": decode_token.get("realm_access", {}).get("roles", []),
            "email": decode_token.get("email", ""),
        }

        if not opa_client.is_allowed(input_data=input_data):
            return Response(content="Forbidden", status_code=403)

        response = await call_next(request)
        return response

    def get_token(self):
        return keycloak_service.get_token("tngiabao", "123")["access_token"]
