from registry.tool_registry import tool_registry
from integrations.integration_service import get_integration_token
import requests


def create_calendar_event(user_context, params):

    user_id = user_context["sub"]

    token = get_integration_token(
        user_id,
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

    response = requests.post(url, headers=headers, json=event)

    return response.json()


tool_registry.register("create_calendar_event", create_calendar_event)