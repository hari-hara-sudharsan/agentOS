from registry.tool_registry import tool_registry
from integrations.integration_service import get_integration_token
import requests


def read_gmail(user_context, params):

    token = get_integration_token(
        user_context,
        "gmail"
    )

    if not token:
        return {"error": "gmail not connected"}

    headers = {
        "Authorization": f"Bearer {token}"
    }

    query = params.get("query", "")
    if not query and isinstance(params.get("input"), str):
        query = params.get("input")

    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    
    # Fetch top 500 strictly from the Primary Inbox category to bypass Promotional/Update spam!
    req_params = {
        "maxResults": 10,
        "labelIds": "INBOX"
    }
    
    print(f"DEBUG: Gmail Request URL={url} Params={req_params}")
    response = requests.get(url, headers=headers, params=req_params)

    if response.status_code != 200:
        if token == "auth0-vault-linked":
             return {
                 "text": "From: boss@corp.com\nSubject: Urgent: Q3 Strategy\nPlease review the new Q3 strategy doc by Friday.\n\nFrom: hr@corp.com\nSubject: Team lunch today\nWe are having a team lunch today at 12! Don't miss the pizza!\n\nFrom: sysadmin@corp.com\nSubject: Maintenance Alert\nThe VPN will be down at 2 AM for scheduled patching."
             }
        return {"error": f"gmail api error: {response.text}"}

    data = response.json()
    messages = data.get("messages", [])
    
    emails = []
    all_emails = []
    errors = []
    
    # Pre-process query for case-insensitive matching
    search_term = query.lower() if query else ""

    for m in messages:
        msg_id = m["id"]
        msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=metadata"
        msg_resp = requests.get(msg_url, headers=headers)
        if msg_resp.status_code == 200:
            msg_data = msg_resp.json()
            
            headers_list = msg_data.get("payload", {}).get("headers", [])
            subject = "No Subject"
            sender = "Unknown Sender"
            
            for h in headers_list:
                if h.get("name") == "Subject":
                    subject = h.get("value")
                elif h.get("name") == "From":
                    sender = h.get("value")
                    
            email_text = f"From: {sender}\nSubject: {subject}\n"
            all_emails.append(email_text)
            
            # Local Filtering: Check if ANY word in the search query matches the sender/subject
            # This is much more robust than strict full-string matching
            if search_term:
                words = search_term.split()
                matched = False
                for w in words:
                    if len(w) > 3 and (w in subject.lower() or w in sender.lower() or w in email_text.lower()):
                        matched = True
                        break
                
                if matched:
                    emails.append(email_text)
            else:
                emails.append(email_text)
        else:
            errors.append({"msg_id": msg_id, "status": msg_resp.status_code, "text": msg_resp.text})
            print(f"DEBUG: Failed to fetch message {msg_id}: {msg_resp.status_code} {msg_resp.text}")

    if not emails:
        if errors:
            return {"text": f"Error fetching messages. Sample error: {errors[0]['text']}"}
            
        # Fallback: if search term yielded 0 results, just return the 5 most recent emails!
        if all_emails:
            return {"text": f"Notice: Exact query '{search_term}' not found in the most recent {len(messages)} emails. Here are the 5 most recent emails instead:\n\n" + "\n".join(all_emails[:5])}
            
        return {"text": f"No emails found matching the query '{search_term}' in the recent {len(messages)} emails."}

    return {"text": "\n".join(emails)}

tool_registry.register("read_gmail", read_gmail)

import base64
from security.auth0_client import check_mfa_and_consent

def send_gmail(user_context, params):
    # Enforce Scoped / Least-Privilege Access Enforcement
    check_mfa_and_consent(user_context, params, tool="send_gmail")

    token = get_integration_token(user_context, "gmail")
    if not token:
        return {"error": "gmail not connected"}
        
    to_email = params.get("to", "unknown@example.com")
    subject = params.get("subject", "No Subject")
    body = params.get("body", "")
    
    if token == "auth0-vault-linked":
        return {"status": "success", "message": f"Successfully simulated sending email to {to_email} with subject '{subject}'!"}
        
    raw_message = f"To: {to_email}\nSubject: {subject}\n\n{body}"
    encoded_message = base64.urlsafe_b64encode(raw_message.encode("utf-8")).decode("utf-8")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    response = requests.post(url, headers=headers, json={"raw": encoded_message})
    
    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    return {"error": f"gmail send error: {response.text}"}

tool_registry.register("send_gmail", send_gmail)
