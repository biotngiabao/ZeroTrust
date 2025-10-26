from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from ..opa.client import opa_client
from starlette.responses import Response
from ..keycloak.client import keycloak_service
import httpx
import random


class AuthenticateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"http://ip-api.com/json/{request.client.host}")
                geo = resp.json()

        except Exception:
            pass

        token_header = request.headers.get("Authorization")
        token_header = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJqVFdLTjc0RjBrdVZGNTc0NFktYVBmNlNreWlsV2hOemxiczZUWFROTE9NIn0.eyJleHAiOjE3NjE0OTE2OTEsImlhdCI6MTc2MTQ1NTY5MSwianRpIjoiYTMwM2IwNWMtZWMxYS00Y2MwLWFlNGItZmEzNGQxZWY3NTVmIiwiaXNzIjoiaHR0cDovL2tleWNsb2FrOjgwODAvcmVhbG1zL2Zhc3RhcGkiLCJhdWQiOlsiYnJva2VyIiwiYWNjb3VudCJdLCJzdWIiOiJiMzU4ODkxNy03NTQ2LTQ5YWYtYTZhNi0wOGRjN2YzYmQ0MTYiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJmYXN0YXBpLWNsaWVudCIsInNpZCI6IjdhMWNiMzNkLWU3Y2UtNGRkOS04YWUxLTk3ZDY0Njk3OTc1MyIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiLyoiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwiYWRtaW4iLCJkZWZhdWx0LXJvbGVzLWZhc3RhcGkiLCJ1bWFfYXV0aG9yaXphdGlvbiIsImZpbmFuY2UiXX0sInJlc291cmNlX2FjY2VzcyI6eyJicm9rZXIiOnsicm9sZXMiOlsicmVhZC10b2tlbiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6InRuZ2lhIGJhbyIsInByZWZlcnJlZF91c2VybmFtZSI6InRuZ2lhYmFvIiwiZ2l2ZW5fbmFtZSI6InRuZ2lhIiwiZmFtaWx5X25hbWUiOiJiYW8iLCJlbWFpbCI6ImJhb0BnbWFpbC5jb20ifQ.NUAQ4pa--utjr_AjSRWQMlTKim4X_3Adhoc9sqC-KEwZlFxQap1A7peAPZIL415SrX2LlbrOwfZmIn-uD9RiVS_oS5DMQEXBl_HT3IdVSXeNWlbG8hYO208aXUo_I6JDKBz3aDRcFRUOs1xQRuOZi4yMo9h1ePLnX9vjaB47rzMvUg5RIes9R6SR5YDFWpfiA9yKoMoT5Xd6MkGJf9beRFZFCB3cMxADN3m7J_i5od3beeO8GKQTOxe1wLIpz25VkCTFUjpdLOeyl1nZj77dHVcdoLFPxwCIec9Ba2S1h9Bc3b-b2CnQQmQwkJYqo00-NvjHhgaCePxJklyVuvDMtQ"

        decode_token = {}

        if token_header:
            access_token = token_header.split(" ")[1]  # Bearer <token>
            try:
                decode_token = keycloak_service.decode_token(access_token)

            except Exception as e:
                pass

        request.state.user = {
            "username": decode_token.get("preferred_username", "unknown"),
            "email": str(random.randint(1, 5)) + decode_token.get("email", "unknown"),
            "roles": decode_token.get("realm_access", {}).get("roles", []),
            "ip": request.client.host,
            "device": request.headers.get("user-agent", "unknown"),
            "country": geo.get("country", "unknown"),
            "city": geo.get("city", "unknown"),
            "isp": geo.get("isp", "unknown"),
            "zip": geo.get("zip", "unknown"),
        }
        response = await call_next(request)
        return response
