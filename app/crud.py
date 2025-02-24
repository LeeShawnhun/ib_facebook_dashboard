# crud.py
from sqlalchemy import distinct, func
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def get_ad(db: Session, ad_id: str):
    return db.query(models.Ad).filter(models.Ad.ad_id == ad_id).first()

def get_ads(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    team: str = None,
    active_only: bool = True
):
    query = db.query(models.Ad)
    if team:
        query = query.filter(models.Ad.team == team)
    if active_only:
        query = query.filter(models.Ad.is_active == True)
    return query.offset(skip).limit(limit).all()

def create_or_update_ad(db: Session, ad: schemas.AdCreate):
    existing_ad = get_ad(db, ad.ad_id)
    
    if existing_ad:
        for key, value in ad.dict(exclude_unset=True).items():
            setattr(existing_ad, key, value)
        existing_ad.last_modified = datetime.utcnow()
    else:
        db_ad = models.Ad(**ad.dict())
        db.add(db_ad)
    
    db.commit()
    return existing_ad if existing_ad else db_ad

def deactivate_old_ads(db: Session, current_ad_ids: list[str]):
    db.query(models.Ad)\
        .filter(models.Ad.is_active == True)\
        .filter(models.Ad.ad_id.notin_(current_ad_ids))\
        .update({models.Ad.is_active: False}, synchronize_session=False)
    db.commit()

def update_ad_comments(db: Session, ad_id: str, comments: schemas.AdUpdate):
    ad = get_ad(db, ad_id)
    if not ad:
        return None
    
    if comments.planner_comment is not None:
        ad.planner_comment = comments.planner_comment
    if comments.executor_comment is not None:
        ad.executor_comment = comments.executor_comment
    ad.last_modified = datetime.utcnow()
    
    db.commit()
    db.refresh(ad)
    return ad

def get_ad_history(
    db: Session,
    team: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    skip: int = 0,
    limit: int = 100
):
    query = db.query(models.Ad)
    
    if team:
        query = query.filter(models.Ad.team == team)
    if start_date:
        query = query.filter(models.Ad.created_at >= start_date)
    if end_date:
        query = query.filter(models.Ad.created_at <= end_date)
        
    # 날짜 기준 내림차순 정렬
    query = query.order_by(models.Ad.created_at.desc())
    
    return query.offset(skip).limit(limit).all()

def get_team_rejection_stats(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(
        models.Ad.team,
        func.count(models.Ad.id).label('total_rejections'),
        func.count(distinct(models.Ad.campaign)).label('affected_campaigns'),
        func.array_agg(distinct(models.Ad.reject_reason)).label('common_reasons')
    ).group_by(models.Ad.team)
    
    if start_date:
        query = query.filter(models.Ad.created_at >= start_date)
    if end_date:
        query = query.filter(models.Ad.created_at <= end_date)
        
    return query.all()