from database.db import SessionLocal
from database.models import AgentAnalytics
from sqlalchemy import func
from datetime import datetime

def record_agent_execution(user_id, task_name, execution_time, status, tool_name=None, error_message=None):
    """Record a tool/agent execution for analytics and activity tracking."""
    db = SessionLocal()
    try:
        analytics = AgentAnalytics(
            user_id=user_id,
            task_name=task_name,
            execution_time=execution_time,
            status=status,
            tool_name=tool_name,
            error_message=error_message
        )
        db.add(analytics)
        db.commit()
    finally:
        db.close()


def get_user_stats(user_id):
    db = SessionLocal()
    try:
        start_of_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        tasks_today = db.query(AgentAnalytics).filter(
            AgentAnalytics.user_id == user_id,
            AgentAnalytics.created_at >= start_of_today
        ).count()

        avg_time = db.query(func.avg(AgentAnalytics.execution_time)).filter(
            AgentAnalytics.user_id == user_id
        ).scalar() or 0.0

        most_used = db.query(AgentAnalytics.task_name, func.count(AgentAnalytics.task_name)).filter(
            AgentAnalytics.user_id == user_id
        ).group_by(AgentAnalytics.task_name).order_by(func.count(AgentAnalytics.task_name).desc()).first()

        success_rate = db.query(
            func.count(AgentAnalytics.id)
        ).filter(
            AgentAnalytics.user_id == user_id,
            AgentAnalytics.status == "success"
        ).scalar() or 0
        
        total = db.query(func.count(AgentAnalytics.id)).filter(
            AgentAnalytics.user_id == user_id
        ).scalar() or 1

        return {
            "tasks_executed_today": tasks_today,
            "average_execution_time": round(float(avg_time), 1),
            "most_used_tool": most_used[0] if most_used else None,
            "success_rate": round((success_rate / total) * 100, 1) if total > 0 else 0
        }
    finally:
        db.close()
