#
# File: middleware/authorize_middleware.py
#
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, RedirectResponse
import base64
from ..opa.client import opa_client
from ..keycloak.client import keycloak_service

logger = logging.getLogger(__name__)


class AuthorizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
    
        user = getattr(request.state, "user", None)
        path = request.url.path
        print("AuthorizeMiddleware - Request Path:", path)

        if user:
            roles = user.get("realm_access", {}).get("roles", [])
            email = user.get("email", "")
            auth_time_value = user.get("auth_time")
            auth_time = auth_time_value if auth_time_value is not None else 0
        else:
            roles = []
            email = ""
            auth_time = 0

        input_data = {
            "method": request.method,
            "path": path.split("/")[1:] if path else [],
            "roles": roles,
            "email": email,
            "authenticated": user is not None ,
            "auth_time": auth_time,
            "key" : request.headers.get("key", "")    
        }
        # if "data.php" in path:
        # print("path", request.url)
        # print("Request Headers:", dict(request.headers))
        try:
            print("OPA Input Data:", input_data)
            decision_result = opa_client.get_decision(input_data)
            decision = decision_result.get("result", {})
            print("OAP decision",decision)
            action = decision.get("action", "deny_forbidden") 
        except Exception as e:
            logger.error(f"Không thể lấy quyết định OPA: {e}")
            action = "deny_forbidden"

        
        if action == "allow":
            return await call_next(request)

        # 2.2: OPA yêu cầu "step-up"
        elif action == "deny_step_up":
            logger.info(f"OPA yêu cầu step-up cho: {path}")
            try:
                original_url = base64.urlsafe_b64encode(str(request.url).encode()).decode()
                redirect_uri = str(request.url_for('auth_callback'))
                base_auth_url = keycloak_service.get_auth_url(
                    redirect_uri, 
                    state=original_url  
                )
                
                auth_url = f"{base_auth_url}&prompt=login"
                return RedirectResponse(url=auth_url, status_code=303)
            except Exception as e:
                logger.error(f"Không thể tạo Keycloak redirect URL cho step-up: {e}")
                return Response(content="Authentication Required", status_code=401)

        elif action == "deny_unauthorized":
            logger.warning(f"OPA Denied (401): {request.method} {path} for user anonymous")
            try:
                original_url = base64.urlsafe_b64encode(str(request.url).encode()).decode()
                redirect_uri = str(request.url_for('auth_callback'))
                auth_url = keycloak_service.get_auth_url(redirect_uri, state=original_url)
                return RedirectResponse(url=auth_url, status_code=303)
            except Exception as e:
                logger.error(f"Không thể tạo Keycloak redirect URL: {e}")
                return Response(content="Authentication Required", status_code=401)
                
        else: 
            logger.warning(f"OPA Denied (403): {request.method} {path} for user {email or 'anonymous'}")
            return Response(content="Forbidden", status_code=403)