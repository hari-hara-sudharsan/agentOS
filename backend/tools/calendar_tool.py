from registry.tool_registry import tool_registry
from integrations.integration_service import get_integration_token
import requests


from security.auth0_client import check_mfa_and_consent

def create_calendar_event(user_context, params):
    # Enforce Scoped / Least-Privilege Access Enforcement
    check_mfa_and_consent(user_context, params, tool="create_calendar_event")

    token = get_integration_token(
        user_context,
        "calendar"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    event = {
        "summary": params.get("title"),
        "start": {"dateTime": params.get("start_time")},
        "end": {"dateTime": params.get("end_time")}
    }

    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

    if token == "auth0-vault-linked":
        return {
            "status": "success",
            "message": f"Successfully simulated adding event '{params.get('title')}' to Calendar!",
            "id": "mock_event_123"
        }

    response = requests.post(url, headers=headers, json=event)

    return response.json()


tool_registry.register("create_calendar_event", create_calendar_event)