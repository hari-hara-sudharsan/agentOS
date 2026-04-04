ALLOWED_ACTIONS = [
    "read_gmail",
    "send_gmail",
    "send_slack_message",
    "create_calendar_event",
    "upload_to_drive",
    "list_drive_files",
    "browser_open_site",
    "browser_login",
    "browser_download_file",
    "browser_scrape_url",
    "browser_search",
    "summarize_text",
    "create_image",
    "create_github_issue",
    "list_github_repos",
    "post_discord_message",
    "create_salesforce_lead",
    "create_linear_issue",
    "create_azure_resource",
    "complete_leetcode_daily",
    "get_leetcode_daily_problem"
]


def check_permission(action):

    if action not in ALLOWED_ACTIONS:
        raise Exception("Tool not allowed")

    return True