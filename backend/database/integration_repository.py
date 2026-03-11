from database.db import SessionLocal
from database.models import Integration


def save_integration(user_id, service, token_reference):

    db = SessionLocal()

    integration = Integration(
        user_id=user_id,
        service=service,
        token_reference=token_reference
    )

    db.add(integration)
    db.commit()

    db.close()


def get_user_integrations(user_id):

    db = SessionLocal()

    integrations = db.query(Integration)\
        .filter(Integration.user_id == user_id).all()

    db.close()

    return integrations


def get_integration_token(user_id, service):

    db = SessionLocal()

    integration = db.query(Integration)\
        .filter(
            Integration.user_id == user_id,
            Integration.service == service
        ).first()

    db.close()

    if integration:
        return integration.token_reference

    return None
