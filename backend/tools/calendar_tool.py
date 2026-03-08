import requests


def create_calendar_event(user_context, params):

    token = user_context.get("calendar_token")

    if not token:
        return {"error": "calendar not connected"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    event = {
        "summary": params.get("title", "AgentOS Event"),
        "start": {
            "dateTime": params.get("start_time")
        },
        "end": {
            "dateTime": params.get("end_time")
        }
    }

    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

    response = requests.post(url, headers=headers, json=event)

    return response.json()