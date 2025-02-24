# main.py
import csv
from datetime import datetime
from io import BytesIO, StringIO
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
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
            return True
            
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

@app.get("/statistics", response_class=HTMLResponse)
async def read_statistics(request: Request):
    return templates.TemplateResponse(
        "statistics.html",
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
    ads = crud.get_ads(
        db, 
        skip=skip, 
        limit=limit, 
        team=team, 
        active_only=active_only
    )
    
    response_data = [
        {
            "id": ad.id,
            "team": ad.team,
            "campaign": ad.campaign,
            "adgroup": ad.adgroup,
            "ad_id": ad.ad_id,
            "ad_name": ad.ad_name,
            "account_name": ad.account_name,
            "reject_reason": ad.reject_reason,
            "planner_comment": ad.planner_comment,
            "executor_comment": ad.executor_comment,
            "last_modified": ad.last_modified,
            "is_active": ad.is_active,
            "created_at": ad.created_at
        } for ad in ads
    ]
    
    return response_data

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
    

@app.get("/ads/export")
def export_ads_csv(
    team: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # 날짜 변환
    start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    
    # 데이터 조회
    ads = crud.get_ad_history(
        db,
        team=team,
        start_date=start_dt,
        end_date=end_dt,
        skip=0,
        limit=None
    )
    
    # CSV 데이터 생성 (명시적으로 쉼표 구분자 지정)
    output = StringIO()
    writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    
    # BOM 추가
    output.write('\ufeff')
    
    # 헤더 작성
    writer.writerow([
        "계정", "캠페인", "광고 그룹", "광고", 
        "거절 사유", "마지막 수정일", "기획팀 의견", "집행팀 의견"
    ])
    
    # 데이터 작성
    for ad in ads:
        writer.writerow([
            ad.account_name,
            ad.campaign,
            ad.adgroup,
            ad.ad_name,
            ad.reject_reason,
            ad.last_modified.strftime("%Y-%m-%d %H:%M:%S") if ad.last_modified else "",
            ad.planner_comment or "",
            ad.executor_comment or ""
        ])
    
    # StringIO의 내용을 UTF-8로 인코딩
    csv_string = output.getvalue()
    
    # 파일 이름 생성
    filename = f"ads_report_{team or 'all'}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        iter([csv_string.encode('utf-8-sig')]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )
    
@app.get("/ads/history", response_model=List[schemas.Ad])
def read_ad_history(
    request: Request,
    team: Optional[str] = None,
    start_date: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db)
):
    # 날짜 문자열을 datetime 객체로 변환
    start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    
    history = crud.get_ad_history(
        db,
        team=team,
        start_date=start_dt,
        end_date=end_dt,
        skip=skip,
        limit=limit
    )
    
    return history

@app.get("/ads/team-stats")
def read_team_stats(
    request: Request,
    start_date: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    
    stats = crud.get_team_rejection_stats(db, start_dt, end_dt)
    
    return {
        "team_stats": [
            {
                "team": stat.team,
                "total_rejections": stat.total_rejections,
                "affected_campaigns": stat.affected_campaigns,
                "common_reasons": stat.common_reasons
            }
            for stat in stats
        ]
    }
    
@app.get("/admin/backup")
async def create_backup():
    success, message = backup.backup_database()
    if success:
        return {"status": "success", "message": message}
    return {"status": "error", "message": message}

@app.get("/admin/restore")
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

@app.put("/ads/{ad_id}/comments")
def update_ad_comments(
    ad_id: str,
    comments: schemas.AdUpdate,
    db: Session = Depends(get_db)
):
    ad = crud.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    updated_ad = crud.update_ad_comments(db, ad_id, comments)
    return updated_ad

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENV") == "development" else False
    )