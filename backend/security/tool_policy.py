SAFE_TOOLS = [
    "read_gmail",
    "summarize_text",
    "list_drive_files",
    "list_github_repos",
    "get_leetcode_daily_problem"
]

RESTRICTED_TOOLS = [
    "browser_open_site",
    "browser_login",
    "browser_download_file",
    "upload_to_drive",
    "send_slack_message",
    "send_gmail",
    "create_image",
    "browser_scrape_url",
    "browser_search",
    "create_calendar_event",
    "create_github_issue",
    "post_discord_message",
    "create_salesforce_lead",
    "create_linear_issue",
    "create_azure_resource",
    "complete_leetcode_daily"
]


def authorize_tool(tool):

    if tool in SAFE_TOOLS:
        return True

    if tool in RESTRICTED_TOOLS:
        return True

    raise Exception("Tool not allowed")
