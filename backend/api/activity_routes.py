from fastapi import APIRouter, Depends
from security.auth0_client import get_current_user
from database.analytics_repository import get_user_stats

router = APIRouter()


from database.db import SessionLocal
from database.models import AgentAnalytics

@router.get("")
def get_activity_log(user=Depends(get_current_user)):
    """Get unified activity log combining tool executions and approvals."""
    user_id = user["sub"]
    db = SessionLocal()
    
    try:
        activity = []
        
        # Get tool executions
        try:
            logs = db.query(AgentAnalytics).filter(
                AgentAnalytics.user_id == user_id
            ).order_by(AgentAnalytics.created_at.desc()).limit(50).all()

            for log in logs:
                activity.append({
                    "id": str(log.id),
                    "type": "tool_execution",
                    "task_name": log.task_name,
                    "status": log.status,
                    "execution_time": round(float(log.execution_time), 1) if log.execution_time else 0,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                    "tool_name": getattr(log, 'tool_name', None),
                    "error": getattr(log, 'error_message', None)
                })
        except Exception as e:
            print(f"DEBUG: Error fetching AgentAnalytics: {e}")
        
        # Get approvals (with error handling in case table doesn't exist)
        try:
            from database.models import Approval
            approvals = db.query(Approval).filter(
                Approval.user_id == user_id
            ).order_by(Approval.created_at.desc()).limit(50).all()
            
            for ap in approvals:
                activity.append({
                    "id": ap.approval_id,
                    "type": "approval",
                    "task_name": f"Approval: {ap.tool}",
                    "status": "approved" if ap.approved else "pending",
                    "execution_time": 0,
                    "created_at": ap.created_at.isoformat() if ap.created_at else None,
                    "tool_name": ap.tool,
                    "binding_message": ap.binding_message,
                    "approved_at": ap.approved_at.isoformat() if ap.approved_at else None
                })
        except Exception as e:
            print(f"DEBUG: Error fetching Approvals (table may not exist): {e}")
        
        # Sort by created_at descending
        activity.sort(key=lambda x: x.get("created_at") or "", reverse=True)
        
        return activity[:50]  # Return top 50
        
    finally:
        db.close()


@router.get("/summary")
def get_activity_summary(user=Depends(get_current_user)):
    """Get activity summary stats."""
    user_id = user["sub"]
    db = SessionLocal()
    
    try:
        # Count total tool executions
        total_executions = 0
        successful = 0
        failed = 0
        pending_approvals = 0
        approved_count = 0
        
        try:
            total_executions = db.query(AgentAnalytics).filter(
                AgentAnalytics.user_id == user_id
            ).count()
            
            successful = db.query(AgentAnalytics).filter(
                AgentAnalytics.user_id == user_id,
                AgentAnalytics.status == "success"
            ).count()
            
            failed = db.query(AgentAnalytics).filter(
                AgentAnalytics.user_id == user_id,
                AgentAnalytics.status == "failed"
            ).count()
        except Exception as e:
            print(f"DEBUG: Error counting AgentAnalytics: {e}")
        
        try:
            from database.models import Approval
            pending_approvals = db.query(Approval).filter(
                Approval.user_id == user_id,
                Approval.approved == False
            ).count()
            
            approved_count = db.query(Approval).filter(
                Approval.user_id == user_id,
                Approval.approved == True
            ).count()
        except Exception as e:
            print(f"DEBUG: Error counting Approvals: {e}")
        
        return {
            "total_executions": total_executions,
            "successful": successful,
            "failed": failed,
            "pending_approvals": pending_approvals,
            "approved_count": approved_count
        }
    finally:
        db.close()


@router.get("/analytics")
def analytics(user=Depends(get_current_user)):
    """Get user analytics stats."""
    user_id = user["sub"]
    stats = get_user_stats(user_id)
    return stats