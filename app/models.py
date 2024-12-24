# models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from app.database import Base
from datetime import datetime

class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    team = Column(String, index=True)
    campaign = Column(String, index=True)
    adgroup = Column(String, index=True)
    ad_id = Column(String, unique=True, index=True)
    ad_name = Column(String, index=True)
    account_name = Column(String, index=True)
    reject_reason = Column(Text)
    last_modified = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)