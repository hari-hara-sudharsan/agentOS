from database.db import SessionLocal
from database.models import AgentAnalytics
from sqlalchemy import func
from datetime import datetime

def record_agent_execution(user_id, task_name, execution_time, status):

    db = SessionLocal()

    analytics = AgentAnalytics(
        user_id=user_id,
        task_name=task_name,
        execution_time=execution_time,
        status=status
    )

    db.add(analytics)
    db.commit()

    db.close()


def get_user_stats(user_id):
    db = SessionLocal()

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

    db.close()

    return {
        "tasks_executed_today": tasks_today,
        "average_execution_time": round(float(avg_time), 1),
        "most_used_tool": most_used[0] if most_used else None
    }
