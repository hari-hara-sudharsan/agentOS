from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database.db import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    auth0_id = Column(String, unique=True)

    email = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)


class Integration(Base):

    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True)

    user_id = Column(String)

    service = Column(String)

    token_reference = Column(String)

    connected_at = Column(DateTime, default=datetime.utcnow)


class ActivityLog(Base):

    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True)

    user_id = Column(String)

    action = Column(String)

    status = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)


class AgentAnalytics(Base):

    __tablename__ = "agent_analytics"

    id = Column(Integer, primary_key=True)

    user_id = Column(String)

    task_name = Column(String)

    execution_time = Column(Integer)

    status = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)