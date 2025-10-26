import httpx


async def geo_lookup_ip(ip_address: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"http://ip-api.com/json/{ip_address}")
            geo = resp.json()
            return geo
    except Exception:
        return {}
