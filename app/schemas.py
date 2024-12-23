# app/schemas.py
from pydantic import BaseModel
from datetime import datetime

class AdBase(BaseModel):
    team: str
    campaign: str
    adgroup: str
    ad: str
    rejectReasaon: str
    lastModified: datetime

class AdCreate(AdBase):
    pass

class Ad(AdBase):
    id: int

    class Config:
        from_attributes = True