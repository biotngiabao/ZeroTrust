from fastapi import FastAPI, Request, Response

from .middleware.logging import SimpleLogMiddleware
from .router import proxy


app = FastAPI()

app.add_middleware(SimpleLogMiddleware)
app.include_router(proxy.router)
