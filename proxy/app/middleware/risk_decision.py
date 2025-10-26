import httpx
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

_last_seen: dict[str, dict[str, any]] = {}


class RiskDecisionMiddleware(BaseHTTPMiddleware):
    def _calc_risk_score(self, user: dict[str, any]) -> int:
        score = 0
        email = user["email"]
        last_info = _last_seen.get(email)

        if last_info:
            if last_info["ip"] != user["ip"]:
                score += 10
            if last_info["device"] != user["device"]:
                score += 20
            if last_info["city"] != user["city"]:
                score += 20
            if last_info["country"] != user["country"]:
                score += 50

        return score

    async def dispatch(self, request: Request, call_next):
        # Implement risk decision logic here
        user = request.state.user

        response = await call_next(request)

        _last_seen[user["email"]] = {
            "ip": user["ip"],
            "device": user["device"],
            "country": user["country"],
            "city": user["city"],
        }

        return response
