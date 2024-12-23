from sqlalchemy.orm import Session
from . import models, schemas

def get_ads_by_team(db: Session, team: str, skip: int = 0, limit: int = 100):
    return db.query(models.User).filter(models.User.team == team)\
        .offset(skip).limit(limit).all()

def create_ad(db: Session, ad: schemas.AdCreate):
    db_ad = models.User(**ad.dict())
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad
