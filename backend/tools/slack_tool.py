import requests


def send_slack_message(user_context, params):

    token = user_context.get("slack_token")

    if not token:
        return {"error": "slack not connected"}

    channel = params.get("channel", "#general")
    message = params.get("message", "AgentOS message")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "channel": channel,
        "text": message
    }

    url = "https://slack.com/api/chat.postMessage"

    response = requests.post(url, headers=headers, json=payload)

    return response.json()