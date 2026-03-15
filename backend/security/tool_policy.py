SAFE_TOOLS = [
    "read_gmail",
    "summarize_text",
    "create_calendar_event"
]

RESTRICTED_TOOLS = [
    "browser_download_file",
    "upload_to_drive",
    "send_slack_message"
]


def authorize_tool(tool):

    if tool in SAFE_TOOLS:
        return True

    if tool in RESTRICTED_TOOLS:
        return True

    raise Exception("Tool not allowed")
