from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from . import crud, schemas
from .meta_api import MetaAdsAPI
from .database import SessionLocal
import pytz

def fetch_and_store_ads():
    meta_api = MetaAdsAPI()
    rejected_ads = meta_api.get_all_rejected_ads()
    
    db = SessionLocal()
    try:
        for ad_data in rejected_ads:
            ad = schemas.AdCreate(**ad_data)
            crud.create_ad(db=db, ad=ad)
    finally:
        db.close()

def init_scheduler():
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Seoul'))  # KST 설정
    scheduler.add_job(
        fetch_and_store_ads, 
        'cron',           
        hour='*',         # 매시 정각
        minute=30         # 38분
    )
    scheduler.start()