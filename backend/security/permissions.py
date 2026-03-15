ALLOWED_ACTIONS = [
    "read_gmail",
    "send_slack_message",
    "create_calendar_event",
    "upload_to_drive",
    "browser_automation"
]


def check_permission(action):

    if action not in ALLOWED_ACTIONS:
        raise Exception("Action not allowed")

    return True