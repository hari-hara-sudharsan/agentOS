from database.db import SessionLocal
from database.models import AgentAnalytics


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

    stats = db.query(AgentAnalytics)\
        .filter(AgentAnalytics.user_id == user_id).all()

    db.close()

    return stats
