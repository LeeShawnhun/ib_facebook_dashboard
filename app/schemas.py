from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AdBase(BaseModel):
    account_name: str
    team: str
    campaign: str
    adgroup: str
    ad_id: str
    ad_name: str
    reject_reason: str
    last_modified: datetime
    is_active: bool = True
    planner_comment: Optional[str] = None
    executor_comment: Optional[str] = None

class AdCreate(AdBase):
    pass

class AdUpdate(BaseModel):
    is_active: Optional[bool] = None
    reject_reason: Optional[str] = None
    last_modified: Optional[datetime] = None
    planner_comment: Optional[str] = None
    executor_comment: Optional[str] = None

class Ad(AdBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True