from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from ..utils import geo_lookup_ip
import httpx
import time
import logging
from logging.handlers import TimedRotatingFileHandler
import os

os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

file_handler = TimedRotatingFileHandler(
    filename="logs/app.log",
    when="midnight",
    backupCount=7,
    encoding="utf-8",
)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    "%Y-%m-%d %H:%M:%S",
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class SimpleLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # skip logging for public paths
        if request.url.path.startswith("/static/") or request.url.path.startswith(
            "/public/"
        ):
            return await call_next(request)

        start = time.time()
        record = {
            "method": request.method,
            "url": str(request.url),
        }

        try:
            response = await call_next(request)
            record["status_code"] = response.status_code
        except Exception as e:
            record["error"] = str(e)
            raise e

        record["risk_score"] = request.state.risk_score
        duration = time.time() - start
        record["duration_ms"] = int(duration * 1000)

        # copy user info from request.state
        for attr in request.state.user:
            record[attr] = request.state.user.get(attr)

        if "error" in record or record.get("status_code", 500) >= 400:
            logger.error(record)
        else:
            logger.info(record)

        return response
