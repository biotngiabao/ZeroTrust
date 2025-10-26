# middleware.py
import time
from typing import Any, Dict, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from ..database.sqlite import get_last_seen, upsert_last_seen


# Middleware to calculate risk score based on user context changes, such as IP, device, and location.
# The risk score is added to the request state for downstream processing.
class CalcRiskMiddleware(BaseHTTPMiddleware):
    async def _calc_risk_score(
        self, last_info: Optional[Dict[str, Any]], user: Dict[str, Any]
    ) -> int:
        """Compare current user context vs last_seen and assign a score."""
        print("Last info:", last_info)
        print("Current user:", user)

        score = 0
        if not last_info:
            return score

        if last_info.get("ip") != user.get("ip"):
            score += 10
        if last_info.get("device") != user.get("device"):
            score += 20
        if last_info.get("city") != user.get("city"):
            score += 20
        if last_info.get("country") != user.get("country"):
            score += 50

        print("Calculated risk score:", score)

        return min(score, 100)

    async def dispatch(self, request: Request, call_next):
        user: Dict[str, Any] = getattr(request.state, "user", {}) or {}
        email = user.get("email")
        ip = user.get("ip")
        device = user.get("device")
        country = user.get("country")
        city = user.get("city")

        if not email or email == "unknown":
            return await call_next(request)

        last_info = await get_last_seen(request.app.state.db, email)

        # Compute risk
        risk_score = await self._calc_risk_score(last_info, user)
        # add risk score to request state
        request.state.risk_score = risk_score

        response = await call_next(request)

        ts = int(time.time())
        await upsert_last_seen(
            request.app.state.db,
            email=email,
            ip=ip or "",
            device=device or "",
            country=country or "",
            city=city or "",
            ts=ts,
        )

        return response
