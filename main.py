from fastapi import FastAPI, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session

from app import models, crud, schemas
from app.database import SessionLocal, engine
from app.scheduler import init_scheduler
from typing import List, Optional
import os
import ipaddress
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# # 환경변수에서 허용 IP 목록 가져오기
# ALLOWED_IPS = os.getenv("ALLOWED_IPS", "").split(",")
# ALLOWED_IP_RANGES = os.getenv("ALLOWED_IP_RANGES", "").split(",")

# class IPRestrictionMiddleware:
#     def __init__(self):
#         self.allowed_ips = set(ip.strip() for ip in ALLOWED_IPS if ip.strip())
#         self.allowed_ip_ranges = []
        
#         # IP 범위 처리
#         for ip_range in ALLOWED_IP_RANGES:
#             if ip_range.strip():
#                 try:
#                     self.allowed_ip_ranges.append(ipaddress.ip_network(ip_range.strip()))
#                 except ValueError as e:
#                     print(f"Invalid IP range format: {ip_range}, error: {e}")

#     async def __call__(self, request: Request, call_next):
#         # 개발 모드에서는 IP 제한 비활성화
#         if os.getenv("ENV") == "development":
#             return await call_next(request)
            
#         # client IP 주소 가져오기
#         client_ip = request.client.host
        
#         # Render의 프록시를 통과한 실제 클라이언트 IP 확인
#         forwarded_for = request.headers.get("x-forwarded-for")
#         if forwarded_for:
#             client_ip = forwarded_for.split(",")[0].strip()
        
#         # IP 검사
#         if not self._is_ip_allowed(client_ip):
#             return JSONResponse(
#                 status_code=403,
#                 content={
#                     "detail": "Access denied. Your IP is not in the allowed list."
#                 }
#             )
        
#         return await call_next(request)
    
#     def _is_ip_allowed(self, ip: str) -> bool:
#         if not self.allowed_ips and not self.allowed_ip_ranges:
#             return True  # IP 제한이 설정되지 않은 경우 모든 접근 허용
            
#         if ip in self.allowed_ips:
#             return True
            
#         try:
#             client_ip = ipaddress.ip_address(ip)
#             for ip_range in self.allowed_ip_ranges:
#                 if client_ip in ip_range:
#                     return True
#         except ValueError:
#             return False
            
#         return False

# FastAPI 애플리케이션 설정
app = FastAPI()

# # 미들웨어 추가
# app.add_middleware(IPRestrictionMiddleware)

# 정적 파일 서빙 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 데이터베이스 초기화
models.Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    init_scheduler()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/ads/", response_model=List[schemas.Ad])
def read_ads(
    skip: int = 0,
    limit: int = 100,
    team: Optional[str] = None,
    db: Session = Depends(get_db)
):
    ads = crud.get_ads_by_team(db, team=team, skip=skip, limit=limit)
    return ads