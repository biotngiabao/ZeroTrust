import time
from typing import Any, Dict, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from ..database.sqlite import get_last_seen, upsert_last_seen

# Cấu hình điểm số cho hành vi truy cập (Dynamic)
SERVICE_WEIGHTS = {
    "/transfer.php": 10,  # Nhạy cảm
    "/admin.php": 15,     # Rất nhạy cảm
    "/data.php": 5,      # Ít rủi ro
    "/dashboard.php": 0, # Rất ít rủi ro
}

MEMORY_CACHE = {} 
CACHE_TTL = 90  # Điểm động sẽ tự reset sau 90 giây 

class CalcRiskMiddleware(BaseHTTPMiddleware):
    
    def _calc_static_risk(self, last_info: Optional[Dict], user: Dict) -> int:
        score = 0
        if not last_info:
            return 0 # Lần đầu tiên user đăng nhập, coi như an toàn 
        

        if last_info.get("ip") != user.get("ip"): score += 10
        if last_info.get("city") != user.get("city"): score += 20
        if last_info.get("device") != user.get("device"): score += 30
        if last_info.get("country") != user.get("country"): score += 50
        
        return min(score, 100)

    def _calc_dynamic_risk(self, email: str, path: str) -> int:
        current_time = int(time.time())
        user_cache = MEMORY_CACHE.get(email, {})

        # Kiểm tra xem điểm cũ còn hạn không 
        if user_cache.get("expire_at", 0) < current_time:
            current_score = 0 # Hết hạn thì reset về 0
        else:
            current_score = user_cache.get("score", 0)

        # Tính điểm cộng thêm dựa trên Path
        added_score = 0
        for svc_path, weight in SERVICE_WEIGHTS.items():
            if path.startswith(svc_path): # Khớp prefix (ví dụ /admin/users cũng dính)
                added_score = weight
                break
        
        new_score = current_score + added_score
        return new_score, added_score

    async def dispatch(self, request: Request, call_next):
        # 1. Lấy thông tin user
        user: Dict[str, Any] = getattr(request.state, "user", {}) or {}
        email = user.get("email")
        
        # Nếu chưa đăng nhập, Risk = 0 
        if not email or email == "unknown":
            request.state.risk_score = 0
            return await call_next(request)

        # 2. Tính Static Risk 
        last_info = await get_last_seen(request.app.state.db, email)
        static_score = self._calc_static_risk(last_info, user)

        # 3. Tính Dynamic Risk 
        dynamic_score, added_score = self._calc_dynamic_risk(email, request.url.path)


        total_risk = static_score + dynamic_score
        
        # Cap điểm ở mức 100
        request.state.risk_score = min(total_risk, 100)

        print(f"User: {email} | Static: {static_score} | Dynamic: {dynamic_score} (+{added_score}) | TOTAL: {request.state.risk_score}")

        # 5. Gửi request đi tiếp 
        response = await call_next(request)


        if 200 <= response.status_code < 400:
            
            if added_score > 0:
                MEMORY_CACHE[email] = {
                    "score": dynamic_score,
                    "expire_at": int(time.time()) + CACHE_TTL
                }

            if static_score < 30: 
                ts = int(time.time())
                await upsert_last_seen(
                    request.app.state.db,
                    email=email,
                    ip=user.get("ip", ""),
                    device=user.get("device", ""),
                    country=user.get("country", ""),
                    city=user.get("city", ""),
                    ts=ts,
                )

        return response