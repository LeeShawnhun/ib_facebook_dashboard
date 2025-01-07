from fastapi import FastAPI, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


from sqlalchemy.orm import Session
from typing import List, Optional
import os
import ipaddress
from dotenv import load_dotenv

from app import models, crud, schemas, backup
from app.database import SessionLocal, engine
from app.scheduler import init_scheduler
from app.meta_api import MetaAdsAPI

# .env 파일 로드
load_dotenv()

# 환경변수에서 허용 IP 목록 가져오기
ALLOWED_IPS = os.getenv("ALLOWED_IPS", "").split(",")
ALLOWED_IP_RANGES = os.getenv("ALLOWED_IP_RANGES", "").split(",")

class IPRestrictionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.allowed_ips = set(ip.strip() for ip in ALLOWED_IPS if ip.strip())
        self.allowed_ip_ranges = []
        
        # IP 범위 처리
        for ip_range in ALLOWED_IP_RANGES:
            if ip_range.strip():
                try:
                    self.allowed_ip_ranges.append(ipaddress.ip_network(ip_range.strip()))
                except ValueError as e:
                    print(f"Invalid IP range format: {ip_range}, error: {e}")

    async def dispatch(self, request: Request, call_next):
        # client IP 주소 가져오기
        client_ip = request.client.host
        
        # Render의 프록시를 통과한 실제 클라이언트 IP 확인
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
            
        # IP 검사
        if not self._is_ip_allowed(client_ip):
            print(f"Access Denied for IP: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={
                    "detail": f"Access denied. Your IP ({client_ip}) is not in the allowed list."
                }
            )
        
        print(f"Access Granted for IP: {client_ip}")
        return await call_next(request)
    
    def _is_ip_allowed(self, ip: str) -> bool:
        if not self.allowed_ips and not self.allowed_ip_ranges:
            return True  # IP 제한이 설정되지 않은 경우 모든 접근 허용
            
        if ip in self.allowed_ips:
            return True
            
        try:
            client_ip = ipaddress.ip_address(ip)
            for ip_range in self.allowed_ip_ranges:
                if client_ip in ip_range:
                    return True
        except ValueError:
            return False
            
        return False

# 터미널에 uvicorn main:app --reload 로 실행
app = FastAPI(title="Meta Ads Monitor")

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IP 제한 미들웨어 추가
app.add_middleware(IPRestrictionMiddleware)

# 정적 파일 서빙 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 데이터베이스 초기화
models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    init_scheduler()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/ads/", response_model=List[schemas.Ad])
def read_ads(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=1000),
    team: Optional[str] = None, 
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db)
):
    """
    광고 목록을 조회합니다.
    - skip: 건너뛸 레코드 수
    - limit: 반환할 최대 레코드 수
    - team: 특정 팀의 광고만 조회
    - active_only: 활성 상태의 광고만 조회
    """
    ads = crud.get_ads(
        db, 
        skip=skip, 
        limit=limit, 
        team=team, 
        active_only=active_only
    )
    return ads

@app.get("/ads/refresh")
async def refresh_ads(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        meta_api = MetaAdsAPI()
        rejected_ads = meta_api.get_all_rejected_ads()
        
        current_ad_ids = []
        
        for ad_data in rejected_ads:
            current_ad_ids.append(ad_data['ad_id'])
            ad = schemas.AdCreate(**ad_data)
            crud.create_or_update_ad(db=db, ad=ad)
        
        crud.deactivate_old_ads(db, current_ad_ids)
        
        return {"status": "success", "message": "Ads refreshed successfully"}
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to refresh ads: {str(e)}"
            }
        )
    
@app.get("/admin/backup")
@app.post("/admin/backup")
async def create_backup():
    success, message = backup.backup_database()
    if success:
        return {"status": "success", "message": message}
    return {"status": "error", "message": message}

@app.get("/admin/restore")
@app.post("/admin/restore")
async def restore_backup():
    success, message = backup.restore_latest_backup()
    if success:
        return {"status": "success", "message": message}
    return {"status": "error", "message": message}

@app.get("/admin/download-backup")
async def download_backup():
    backup_files = [f for f in os.listdir('./backups') if f.startswith('db_backup_')]
    if not backup_files:
        return {"error": "No backup files found"}
        
    latest_backup = max(backup_files)
    file_path = os.path.join('./backups', latest_backup)
    
    return FileResponse(
        path=file_path,
        filename=latest_backup,
        media_type='application/octet-stream'
    )

@app.get("/test-ip")
async def test_ip(request: Request):
    client_ip = request.client.host
    forwarded_for = request.headers.get("x-forwarded-for")
    
    return {
        "client_ip": client_ip,
        "x-forwarded-for": forwarded_for,
        "is_allowed": client_ip in ALLOWED_IPS or any(
            ipaddress.ip_address(client_ip) in ipaddress.ip_network(range)
            for range in ALLOWED_IP_RANGES if range.strip()
        )
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENV") == "development" else False
    )