from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
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

    # Non-sensitive linkage reference (Auth0 identity provider reference), never raw access/refresh tokens.
    token_reference = Column(String)
    
    # Extra data for services that need more than a token (e.g., LeetCode username)
    extra_data = Column(Text, nullable=True)

    connected_at = Column(DateTime, default=datetime.utcnow)


class ActivityLog(Base):

    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True)

    user_id = Column(String, index=True)

    action = Column(String)

    status = Column(String)

    details = Column(Text, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class AgentAnalytics(Base):

    __tablename__ = "agent_analytics"

    id = Column(Integer, primary_key=True)

    user_id = Column(String, index=True)

    task_name = Column(String)
    
    tool_name = Column(String, nullable=True)  # Tool that was executed
    
    error_message = Column(Text, nullable=True)  # Error details if failed

    execution_time = Column(Integer)

    status = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class Approval(Base):
    """
    Human-in-the-loop approvals for high-stakes agent actions.
    Persisted to database (not in-memory) to survive restarts.
    """
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True)
    
    approval_id = Column(String, unique=True, index=True)  # UUID for API reference
    
    user_id = Column(String, index=True)
    
    tool = Column(String)  # Tool requiring approval (send_gmail, create_calendar_event, etc.)
    
    params = Column(Text)  # JSON-serialized parameters
    
    binding_message = Column(Text)  # Human-readable description of action
    
    approved = Column(Boolean, default=False)
    
    approved_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    expires_at = Column(DateTime)  # 30-minute expiration