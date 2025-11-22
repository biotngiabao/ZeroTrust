from .middleware.authenticate import AuthenticateMiddleware
from .middleware.authorize import AuthorizeMiddleware
from fastapi import FastAPI, Request, Response, HTTPException

from .middleware.logging import SimpleLogMiddleware
from .middleware.authorize import AuthorizeMiddleware
from .middleware.authenticate import AuthenticateMiddleware
from .middleware.risk_decision import CalcRiskMiddleware
from .router import proxy

from fastapi.responses import JSONResponse, RedirectResponse

from .keycloak.client import keycloak_service
from pydantic import BaseModel
import base64
from .database.sqlite import init_db

app = FastAPI()


@app.on_event("startup")
async def _startup():
    await init_db(app)


class TokenRequest(BaseModel):
    username: str
    password: str


@app.post("/token")
async def get_token(payload: TokenRequest):
    try:
        return keycloak_service.get_token(
            username=payload.username,
            password=payload.password,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to obtain token: {e}")


@app.get("/auth/callback", name="auth_callback")
async def auth_callback(request: Request, code: str, state: str | None = None):
    try:
        redirect_uri = str(request.url_for("auth_callback"))
        token_data = keycloak_service.keycloak_openid.token(
            grant_type="authorization_code", code=code, redirect_uri=redirect_uri
        )
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=400, detail="Could not retrieve access token"
            )

        redirect_to_url = "/"
        if state:
            try:
                redirect_to_url = base64.urlsafe_b64decode(state).decode()
            except Exception:
                redirect_to_url = "/"

        response = RedirectResponse(url=redirect_to_url)
        response.set_cookie(
            key="access_token", value=access_token, httponly=True, samesite="lax"
        )
        return response
    except Exception as e:
        return JSONResponse(
            content={"error": "Failed to obtain token", "detail": str(e)},
            status_code=400,
        )


app.add_middleware(AuthorizeMiddleware)
app.add_middleware(SimpleLogMiddleware)
app.add_middleware(CalcRiskMiddleware)
app.add_middleware(AuthenticateMiddleware)


app.include_router(proxy.router)
