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
        "maxResults": 500,
        "labelIds": "INBOX"
    }
    
    print(f"DEBUG: Gmail Request URL={url} Params={req_params}")
    response = requests.get(url, headers=headers, params=req_params)

    if response.status_code != 200:
        if token == "auth0-vault-linked":
             return {"error": "gmail api error: Your backend was unable to securely retrieve the Google access token from the Auth0 Token Vault Management API. Please ensure your Auth0 backend application has the 'read:user_idp_tokens' and 'read:users' Management API permissions enabled under APIs -> Machine to Machine Applications in the Auth0 Dashboard!"}
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
