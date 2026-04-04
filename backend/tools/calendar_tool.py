from registry.tool_registry import tool_registry
from integrations.integration_service import get_integration_token
from security.auth0_client import check_mfa_and_consent
import requests
from datetime import datetime, timedelta
import re


def parse_datetime(time_str):
    """Parse natural language or ISO datetime strings."""
    if not time_str:
        return None
    
    # If already ISO format, return as-is
    if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', time_str):
        # Ensure timezone
        if not time_str.endswith('Z') and '+' not in time_str and '-' not in time_str[-6:]:
            time_str += '+00:00'
        return time_str
    
    now = datetime.now()
    time_lower = time_str.lower()
    
    # Parse relative dates
    if 'tomorrow' in time_lower:
        base_date = now + timedelta(days=1)
    elif 'today' in time_lower:
        base_date = now
    elif 'next week' in time_lower:
        base_date = now + timedelta(days=7)
    else:
        base_date = now
    
    # Parse time
    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_lower)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        meridiem = time_match.group(3)
        
        if meridiem == 'pm' and hour < 12:
            hour += 12
        elif meridiem == 'am' and hour == 12:
            hour = 0
        
        base_date = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    return base_date.isoformat()


def create_calendar_event(user_context, params):
    """Create a Google Calendar event. Requires step-up auth for security."""
    
    # Enforce Scoped / Least-Privilege Access Enforcement (HIGH-STAKES ACTION)
    check_mfa_and_consent(user_context, params, tool="create_calendar_event")

    token = get_integration_token(user_context, "calendar")

    if not token:
        return {
            "error": "calendar_not_connected",
            "message": "Google Calendar is not connected. Please authorize Calendar access.",
            "steps": [
                "1. Go to the Integrations page",
                "2. Click 'Authorize Vault Access' on the Calendar card",
                "3. Allow calendar permissions in the Google consent screen",
                "4. Try your request again"
            ]
        }

    if token == "auth0-vault-linked":
        return {
            "error": "calendar_token_not_resolved",
            "message": "Calendar integration is linked but token could not be resolved. Please reconnect.",
            "steps": [
                "1. Go to the Integrations page",
                "2. Click 'Disconnect' on Calendar",
                "3. Click 'Authorize Vault Access' again"
            ]
        }

    # Parse datetime strings
    title = params.get("title", "New Event")
    start_time = parse_datetime(params.get("start_time"))
    end_time = parse_datetime(params.get("end_time"))
    
    # Default end time to 1 hour after start
    if start_time and not end_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = start_dt + timedelta(hours=1)
            end_time = end_dt.isoformat()
        except:
            end_time = start_time  # Fallback
    
    if not start_time:
        return {
            "error": "invalid_parameters",
            "message": "Could not parse start_time. Please provide a valid datetime.",
            "example": "Create a meeting tomorrow at 3pm called Team Standup"
        }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    event = {
        "summary": title,
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"}
    }
    
    # Add description if provided
    if params.get("description"):
        event["description"] = params.get("description")

    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

    print(f"DEBUG: Creating calendar event: {event}")
    response = requests.post(url, headers=headers, json=event)

    if response.status_code == 401:
        # Token expired - purge and ask for re-auth
        try:
            from database.db import SessionLocal
            from database.models import Integration
            db = SessionLocal()
            db.query(Integration).filter(
                Integration.user_id == user_context["sub"], 
                Integration.service == "calendar"
            ).delete()
            db.commit()
            db.close()
            print(f"DEBUG: Purged expired Calendar token")
        except Exception as e:
            print(f"DEBUG: Failed to purge token: {e}")
            
        return {
            "error": "calendar_token_expired",
            "message": "Your Calendar access token has expired. Please reconnect.",
            "steps": [
                "1. Go to the Integrations page",
                "2. Calendar should show as 'Disconnected'",
                "3. Click 'Authorize Vault Access' to reconnect"
            ]
        }
    
    if response.status_code == 403:
        return {
            "error": "calendar_permission_denied",
            "message": "Permission denied. Make sure you granted calendar.events scope.",
            "details": response.text,
            "steps": [
                "1. Go to the Integrations page",
                "2. Disconnect and reconnect Calendar",
                "3. Ensure you check the Calendar permissions checkbox"
            ]
        }
    
    if response.status_code not in [200, 201]:
        return {
            "error": "calendar_api_error",
            "message": f"Calendar API error: {response.status_code}",
            "details": response.text
        }

    result = response.json()
    return {
        "status": "success",
        "message": f"✅ Event '{title}' created successfully!",
        "event_id": result.get("id"),
        "link": result.get("htmlLink"),
        "start": result.get("start", {}).get("dateTime"),
        "end": result.get("end", {}).get("dateTime")
    }


tool_registry.register("create_calendar_event", create_calendar_event)