# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from . import crud, schemas, backup
from .meta_api import MetaAdsAPI
from .database import SessionLocal
import pytz

def fetch_and_store_ads():
    meta_api = MetaAdsAPI()
    rejected_ads = meta_api.get_all_rejected_ads()
    
    db = SessionLocal()
    try:
        current_ad_ids = []
        for ad_data in rejected_ads:
            current_ad_ids.append(ad_data['ad_id'])
            ad = schemas.AdCreate(**ad_data)
            crud.create_or_update_ad(db=db, ad=ad)
        
        crud.deactivate_old_ads(db, current_ad_ids)
    finally:
        db.close()

def init_scheduler():
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Seoul'))
    
    # 기존 광고 데이터 수집 작업
    scheduler.add_job(
        fetch_and_store_ads, 
        'cron',
        hour='*',
        minute=30
    )
    
    # DB 백업 작업 (매일 자정에 실행)
    scheduler.add_job(
        backup.backup_database,
        'cron',
        hour=0,
        minute=0
    )
    
    scheduler.start()