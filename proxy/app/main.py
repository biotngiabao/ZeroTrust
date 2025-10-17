from fastapi import FastAPI, Request, Response,  HTTPException

from .middleware.logging import SimpleLogMiddleware

from .middleware.auth import AuthMiddleware

from .router import proxy

from fastapi.responses import JSONResponse, RedirectResponse 

from .keycloak.client import keycloak_service
from pydantic import BaseModel
import base64
app = FastAPI()


class TokenRequest(BaseModel):
    username: str
    password: str

@app.post("/token")
async def get_token(payload: TokenRequest):
    return keycloak_service.get_token(
        username=payload.username,
        password=payload.password,
    )
@app.get("/auth/callback", name="auth_callback")
async def auth_callback(request: Request, code: str, state: str | None = None):
    try:
        redirect_uri = str(request.url_for('auth_callback'))
        token_data = keycloak_service.keycloak_openid.token(
            grant_type='authorization_code', code=code, redirect_uri=redirect_uri
        )
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Could not retrieve access token")
            
        redirect_to_url = "/" 
        if state:
            try:
                redirect_to_url = base64.urlsafe_b64decode(state).decode()
            except Exception:
                redirect_to_url = "/"

        response = RedirectResponse(url=redirect_to_url)
        response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax")
        return response
    except Exception as e:
        return JSONResponse(content={"error": "Failed to obtain token", "detail": str(e)}, status_code=400)

app.add_middleware(SimpleLogMiddleware)
app.add_middleware(AuthMiddleware)

app.include_router(proxy.router)
