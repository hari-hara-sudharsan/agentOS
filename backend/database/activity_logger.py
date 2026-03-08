from database.db import SessionLocal
from database.models import ActivityLog


def log_activity(user_id, action, status):

    db = SessionLocal()

    log = ActivityLog(
        user_id=user_id,
        action=action,
        status=status
    )

    db.add(log)

    db.commit()

    db.close()