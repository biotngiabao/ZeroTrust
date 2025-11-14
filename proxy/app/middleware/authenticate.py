#
# File: middleware/authenticate_middleware.py
#
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from keycloak.exceptions import KeycloakInvalidTokenError


from ..keycloak.client import keycloak_service

logger = logging.getLogger(__name__)

class AuthenticateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        request.state.user = None
        
        # 2. Lấy token từ cookie
        access_token = request.cookies.get("access_token")

        if not access_token:
            auth_header = request.headers.get("authorization") 
            if auth_header and auth_header.startswith("Bearer "):
                access_token = auth_header.split(" ")[1]
                
        if access_token:
            try:

                decode_token = keycloak_service.decode_token(access_token)
                

                request.state.user = decode_token
                
            except KeycloakInvalidTokenError:

                logger.warning("Invalid access token found in cookie.")
                request.state.user = None
            except Exception as e:

                logger.exception(f"Unexpected error during token decoding: {e}")
                request.state.user = None


        response = await call_next(request)
        return response