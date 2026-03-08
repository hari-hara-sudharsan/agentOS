from pydantic import BaseModel
from datetime import datetime


class ActivityLogSchema(BaseModel):

    user_id: str
    action: str
    status: str
    timestamp: datetime

    class Config:
        orm_mode = True