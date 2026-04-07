from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
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
    Enhanced with Consent Guardian and Scope Weaver analysis.
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
    
    expires_at = Column(DateTime)  # 24-hour expiration
    
    # Consent Guardian analysis fields (JSON-serialized)
    openclaw_analysis = Column(Text, nullable=True)  # Full analysis JSON from Consent Guardian
    
    risk_level = Column(String, nullable=True)  # low, medium, high, critical
    
    recommended_scopes = Column(Text, nullable=True)  # JSON list of minimal scopes recommended
    
    ai_explanation = Column(Text, nullable=True)  # Plain English explanation from OpenClaw
    
    analysis_confidence = Column(String, nullable=True)  # Analysis confidence score
    
    # Scope Weaver fields
    scope_weaver_analysis = Column(Text, nullable=True)  # Full Scope Weaver JSON
    
    scope_evolution_score = Column(Integer, nullable=True)  # 0-100 scope reduction score
    
    original_scopes = Column(Text, nullable=True)  # JSON list of original scopes before weaving
    
    # Shadow Simulator fields
    shadow_simulation = Column(Text, nullable=True)  # Full Shadow Simulation JSON
    
    shadow_simulation_id = Column(String, nullable=True)  # Simulation ID for tracking
    
    shadow_outcome = Column(String, nullable=True)  # success, caution, warning, blocked
    
    shadow_confidence = Column(Float, nullable=True)  # Simulation confidence score
    
    shadow_risk_count = Column(Integer, nullable=True)  # Number of risks identified


class ScopeWeaverPattern(Base):
    """
    Stores non-sensitive scope patterns for learning.
    
    SECURITY: Never stores tokens or secrets - only action→scope mappings.
    This allows the system to learn optimal scope recommendations over time.
    """
    __tablename__ = "scope_weaver_patterns"
    
    id = Column(Integer, primary_key=True)
    
    user_id = Column(String, index=True)  # For per-user patterns (optional)
    
    tool_name = Column(String, index=True)  # e.g., "send_gmail"
    
    action_type = Column(String, index=True)  # e.g., "write", "read", "auth"
    
    recommended_scopes = Column(Text)  # JSON list of minimal scopes
    
    original_scopes = Column(Text)  # JSON list of original scopes
    
    scope_evolution_score = Column(Integer)  # 0-100 reduction achieved
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Outcome tracking (did the reduced scopes work?)
    execution_succeeded = Column(Boolean, nullable=True)
    
    # Confidence score from OpenClaw analysis
    confidence = Column(Float, nullable=True)


class ShadowSimulation(Base):
    """
    Stores shadow simulation results for analytics.
    
    SECURITY: Never stores tokens or secrets - only simulation metadata
    and outcomes for risk analysis and learning.
    """
    __tablename__ = "shadow_simulations"
    
    id = Column(Integer, primary_key=True)
    
    simulation_id = Column(String, unique=True, index=True)
    
    user_id = Column(String, index=True)
    
    tool_name = Column(String, index=True)
    
    outcome = Column(String)  # success, caution, warning, blocked
    
    risk_count = Column(Integer, default=0)
    
    has_high_risks = Column(Boolean, default=False)
    
    confidence_score = Column(Float)
    
    user_decision = Column(String)  # executed, cancelled, modified
    
    simulation_duration_ms = Column(Integer)
    
    explanation = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)