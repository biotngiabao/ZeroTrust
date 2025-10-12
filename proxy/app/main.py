from fastapi import FastAPI, Request, Response

from .middleware.logging import SimpleLogMiddleware
from .middleware.auth import AuthMiddleware
from .router import proxy
from .keycloak.client import keycloak_service
from pydantic import BaseModel


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


app.add_middleware(SimpleLogMiddleware)
app.add_middleware(AuthMiddleware)

app.include_router(proxy.router)
