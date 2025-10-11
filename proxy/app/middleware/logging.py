from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SimpleLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method
        response = await call_next(request)
        print(f"{method} {path} -> {response.status_code}")
        return response
