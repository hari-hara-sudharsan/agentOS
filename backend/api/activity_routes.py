from fastapi import APIRouter, Depends
from security.auth0_client import get_current_user
from database.analytics_repository import get_user_stats

router = APIRouter()


from database.db import SessionLocal
from database.models import AgentAnalytics

@router.get("/")
def get_activity_log(user=Depends(get_current_user)):

    user_id = user["sub"]
    db = SessionLocal()
    
    logs = db.query(AgentAnalytics).filter(
        AgentAnalytics.user_id == user_id
    ).order_by(AgentAnalytics.created_at.desc()).limit(20).all()

    activity = []
    for log in logs:
        activity.append({
            "task_name": log.task_name,
            "status": log.status,
            "execution_time": round(float(log.execution_time), 1)
        })
        
    db.close()
    return activity

@router.get("/analytics")
def analytics(user=Depends(get_current_user)):

    user_id = user["sub"]

    stats = get_user_stats(user_id)

    return stats