# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.requests import Request
# from ..opa.client import opa_client
# from starlette.responses import Response
# from ..keycloak.client import keycloak_service
# from fastapi.responses import RedirectResponse
# PUBLIC_EXACT = {"/docs", "/openapi.json", "/docs/oauth2-redirect", "/healthz", "/token"}
# PUBLIC_PREFIXES = (
#     "/static/",
#     "/public/",
#     "/index.php"
# )


# class AuthMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         path = request.url.path

#         if path in PUBLIC_EXACT or path.startswith(PUBLIC_PREFIXES):
#             return await call_next(request)

#         access_token = None
        
#         # 1. Ưu tiên kiểm tra "vé giấy" (Authorization header) - dành cho các API client
#         token_header = request.headers.get("Authorization")
#         if token_header:
#             parts = token_header.split()
#             if len(parts) == 2 and parts[0].lower() == "bearer":
#                 access_token = parts[1]
        
#         # 2. Nếu không có header, kiểm tra "vòng tay" (cookie) - dành cho trình duyệt web
#         if not access_token:
#             access_token = request.cookies.get("access_token")

#         # 3. Nếu vẫn không có gì cả, mới chuyển hướng đi đăng nhập
#         if not access_token:
#             redirect_uri = str(request.url_for('auth_callback'))
#             auth_url = keycloak_service.get_auth_url(redirect_uri)
#             return RedirectResponse(url=auth_url, status_code=307)

#         # print(decode_token)

#         input_data = {
#             "method": request.method,
#             "path": path.split("/")[1:] if path else [],
#             "roles": decode_token.get("realm_access", {}).get("roles", []),
#             "email": decode_token.get("email", ""),
#         }

#         if not opa_client.is_allowed(input_data=input_data):
#             return Response(content="Forbidden", status_code=403)

#         response = await call_next(request)
#         return response

#     def get_token(self):
#         return keycloak_service.get_token("tngiabao", "123")["access_token"]



import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, RedirectResponse
from ..opa.client import opa_client
# from ..keycloak.client import get_keycloak_service # Sử dụng hàm để lazy loading
from ..keycloak.client import keycloak_service
from keycloak.exceptions import KeycloakInvalidTokenError
import base64

logger = logging.getLogger(__name__)


PUBLIC_EXACT = {"/docs", "/openapi.json", "/docs/oauth2-redirect", "/healthz", "/token", "/auth/callback"}
PUBLIC_PREFIXES = ("/static/", 
                   "/public/",
                     "/index.php"
                   )

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in PUBLIC_EXACT or path.startswith(PUBLIC_PREFIXES):
            return await call_next(request)

        access_token = request.cookies.get("access_token")

        if not access_token:

            original_url = base64.urlsafe_b64encode(str(request.url).encode()).decode()
            
            redirect_uri = str(request.url_for('auth_callback'))
            
            auth_url = keycloak_service.get_auth_url(redirect_uri, state=original_url)
            
            return RedirectResponse(url=auth_url, status_code=307)

        try:
            decode_token = keycloak_service.decode_token(access_token)
        except KeycloakInvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            response = RedirectResponse(url=request.url, status_code=307)
            response.delete_cookie("access_token")
            return response
        except Exception as e:
            logger.exception(f"Unexpected error during token decoding: {e}")
            return JSONResponse(content={"detail": "Error decoding token"}, status_code=500)

        input_data = {
            "method": request.method,
            "path": path.split("/")[1:] if path else [],
            "roles": decode_token.get("realm_access", {}).get("roles", []),
            "email": decode_token.get("email", ""),
        }

        if not opa_client.is_allowed(input_data=input_data):
            return Response(content="Forbidden", status_code=403)

        return await call_next(request)