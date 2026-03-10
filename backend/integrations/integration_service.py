from database.db import SessionLocal
from database.models import Integration


def save_integration(user_id, service, access_token):

    db = SessionLocal()

    integration = Integration(
        user_id=user_id,
        service=service,
        access_token=access_token
    )

    db.add(integration)
    db.commit()

    db.close()


def get_integration_token(user_id, service):

    db = SessionLocal()

    integration = db.query(Integration)\
        .filter(
            Integration.user_id == user_id,
            Integration.service == service
        ).first()

    db.close()

    if integration:
        return integration.access_token

    return None