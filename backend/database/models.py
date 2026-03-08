from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from database.db import Base


class ActivityLog(Base):

    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String)

    action = Column(String)

    status = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)