from fastapi import FastAPI, Request, Response

from .middleware.logging import SimpleLogMiddleware
from .middleware.authorize import AuthorizeMiddleware
from .middleware.authenticate import AuthenticateMiddleware
from .middleware.risk_decision import CalcRiskMiddleware
from .router import proxy
from .keycloak.client import keycloak_service
from pydantic import BaseModel
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
    return keycloak_service.get_token(
        username=payload.username,
        password=payload.password,
    )


app.add_middleware(AuthorizeMiddleware)
app.add_middleware(SimpleLogMiddleware)
app.add_middleware(CalcRiskMiddleware)
app.add_middleware(AuthenticateMiddleware)


app.include_router(proxy.router)
