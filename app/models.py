from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class User(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    team = Column(String, index=True)
    campaign = Column(String, index=True)
    adgroup = Column(String, index=True)
    ad = Column(String, unique=True, index=True)
    rejectReasaon = Column(String, index=True)
    lastModified = Column(DateTime)
