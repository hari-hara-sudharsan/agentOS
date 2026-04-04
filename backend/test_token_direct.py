import os
import requests

def test_token(token: str):
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"maxResults": 5, "labelIds": "INBOX"}
    r = requests.get(url, headers=headers, params=params)
    print(r.status_code, r.text)

if __name__ == "__main__":
    token = os.environ.get("GMAIL_ACCESS_TOKEN")
    if not token:
        raise SystemExit("Set GMAIL_ACCESS_TOKEN env var (do NOT hardcode tokens).")
    test_token(token)
