from registry.tool_registry import tool_registry
from integrations.integration_service import get_integration_token
import requests
import datetime


def read_gmail(user_context, params):

    token = get_integration_token(
        user_context,
        "gmail"
    )

    print(f"DEBUG: read_gmail - token type: {type(token)}, token value: {token[:50] if token and len(token) > 50 else token}")

    if not token:
        return {
            "error": "gmail_not_connected",
            "message": "Gmail is not connected to the AgentOS Vault. The stale session has been cleared.",
            "steps": [
                "1. Go to the Integrations page",
                "2. Click 'Authorize Vault Access' on the Gmail card",
                "3. Ensure you check the Gmail checkboxes in the popup",
                "4. If the popup is blocked, allow it in your browser address bar",
                "5. FAIL-SAFE: If the button still fails, use the 'Manual Token Override' box on the card."
            ]
        }

    # Basic token validation
    if not isinstance(token, str) or len(token.strip()) == 0:
        return {
            "error": "gmail_token_invalid",
            "message": "Gmail integration token is malformed or expired. Please reconnect your Gmail account.",
            "steps": [
                "1. Go to the Integrations page",
                "2. Find 'Gmail' and click 'Disconnect'",
                "3. Click 'Connect' again",
                "4. Complete the Google OAuth flow"
            ],
            "details": "The stored token is empty or invalid. This requires re-authorization."
        }

    if token == "auth0-vault-linked":
        # Auth0 vault link exists but direct token access hasn’t been resolved.
        return {
            "error": "gmail_token_not_resolved",
            "message": "Gmail integration is linked via Auth0 but the access token could not be resolved. Please reconnect your account to refresh our vault access.",
            "steps": [
                "1. Go to the Integrations page",
                "2. Click 'Disconnect' on Gmail",
                "3. Click 'Authorize Vault Access' to restart the flow"
            ]
        }

    headers = {
        "Authorization": f"Bearer {token}"
    }

    query = params.get("query", "")
    if not query and isinstance(params.get("input"), str):
        query = params.get("input")

    # Convert date queries to Gmail search syntax
    gmail_query = ""
    search_term = query.lower() if query else ""
    
    import datetime
    today = datetime.date.today()
    
    # Check if query is already Gmail search syntax
    if "after:" in search_term or "before:" in search_term or "from:" in search_term or "to:" in search_term or "subject:" in search_term:
        # Use the query directly as Gmail search syntax
        gmail_query = query
    elif "today" in search_term or "today's" in search_term:
        # Format: after:2026/03/29 before:2026/03/30
        yesterday = today - datetime.timedelta(days=1)
        gmail_query = f"after:{yesterday.strftime('%Y/%m/%d')} before:{today.strftime('%Y/%m/%d')}"
    elif "yesterday" in search_term:
        day_before = today - datetime.timedelta(days=2)
        yesterday = today - datetime.timedelta(days=1)
        gmail_query = f"after:{day_before.strftime('%Y/%m/%d')} before:{yesterday.strftime('%Y/%m/%d')}"
    elif any(word in search_term for word in ["week", "this week"]):
        week_start = today - datetime.timedelta(days=today.weekday())
        week_end = week_start + datetime.timedelta(days=7)
        gmail_query = f"after:{week_start.strftime('%Y/%m/%d')} before:{week_end.strftime('%Y/%m/%d')}"
    elif any(word in search_term for word in ["month", "this month"]):
        month_start = today.replace(day=1)
        next_month = month_start.replace(month=month_start.month % 12 + 1, year=month_start.year + (month_start.month // 12))
        gmail_query = f"after:{month_start.strftime('%Y/%m/%d')} before:{next_month.strftime('%Y/%m/%d')}"
    
    # Extract sender filter if present (e.g., "from jpmorgan")
    sender_filter = None
    for keyword in ["from ", "from:"]:
        if keyword in search_term:
            idx = search_term.index(keyword)
            rest = search_term[idx + len(keyword):].strip()
            sender_filter = rest.split()[0] if rest.split() else None
            if sender_filter:
                gmail_query = f"{gmail_query} from:{sender_filter}".strip()

    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    
    # Use Gmail search query if we have date filtering
    req_params = {
        "maxResults": 50,  # Increased to get more emails for date ranges
        "labelIds": "INBOX"
    }
    
    if gmail_query:
        req_params["q"] = gmail_query
    
    print(f"DEBUG: Gmail Request URL={url} Params={req_params}")
    response = requests.get(url, headers=headers, params=req_params)

    if response.status_code != 200:
        print(f"DEBUG: Gmail API error: {response.status_code} {response.text}")
        # Check for authentication errors
        if response.status_code == 401:
            # Token expired - purge the stale integration to force re-auth
            try:
                from database.db import SessionLocal
                from database.models import Integration
                db = SessionLocal()
                db.query(Integration).filter(Integration.user_id == user_context["sub"], Integration.service == "gmail").delete()
                db.commit()
                db.close()
                print(f"DEBUG: Purged expired Gmail token for {user_context['sub']}")
            except Exception as purge_err:
                print(f"DEBUG: Failed to purge expired token: {purge_err}")
                
            return {
                "error": "gmail_token_expired",
                "message": "Your Gmail access token has expired and has been cleared. Please reconnect your account.",
                "steps": [
                    "1. Go to the Integrations page in your dashboard",
                    "2. Gmail should now show as 'Disconnected'",
                    "3. Click 'Authorize Vault Access' to reconnect",
                    "4. Try your request again"
                ]
            }
        elif response.status_code == 403:
            details = response.text
            if "Metadata scope does not support 'q' parameter" in details:
                # BREAK THE LOOP: If we detect Metadata Only, delete the integration record from our DB.
                # This forces the system to forget the stale token and ask for a new one.
                try:
                    from database.db import SessionLocal
                    from database.models import Integration
                    db = SessionLocal()
                    db.query(Integration).filter(Integration.user_id == user_context["sub"], Integration.service == "gmail").delete()
                    db.commit()
                    db.close()
                    print(f"DEBUG: Successfully purged stale Gmail token for {user_context['sub']}")
                except Exception as purge_err:
                    print(f"DEBUG: Failed to purge stale token: {purge_err}")

                return {
                    "error": "gmail_permission_denied_stale_session",
                    "message": "STALE SESSION PURGED: Your Gmail permissions were stuck in 'Metadata Only' mode. I have now cleared the invalid connection.",
                    "steps": [
                        "1. Go to the Integrations page",
                        "2. You should see Gmail as 'Disconnected' now.",
                        "3. Click 'Authorize Vault Access'",
                        "4. YOU MUST: Check the checkbox on the Google consent screen to allow reading/sending emails."
                    ]
                }
            
            return {
                "error": "gmail_permission_denied",
                "message": "The agent lacks the necessary permissions to read your Gmail (gmail.readonly scope).",
                "details": details,
                "steps": [
                    "1. Go to the Integrations page",
                    "2. Click 'Revoke' on the Google/Gmail card",
                    "3. Click 'Authorize Vault Access' and make sure to 'Allow' the application to read emails."
                ]
            }
        else:
            return {
                "error": "gmail_api_error",
                "message": f"Gmail API error: {response.status_code}",
                "details": response.text,
                "steps": [
                    "1. Check your internet connection",
                    "2. Try disconnecting and reconnecting Gmail from Integrations",
                    "3. If error persists, contact support"
                ]
            }

    data = response.json()
    print(f"DEBUG: Gmail API success: found {len(data.get('messages', []))} messages")
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
            
            # If we used API-level filtering (gmail_query set), include all emails
            # Otherwise, do client-side filtering
            if gmail_query:
                emails.append(email_text)
            elif search_term:
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
    """Send an email via Gmail. HIGH-STAKES action requiring human approval."""
    # Enforce Scoped / Least-Privilege Access Enforcement
    check_mfa_and_consent(user_context, params, tool="send_gmail")

    token = get_integration_token(user_context, "gmail")
    
    if not token:
        return {
            "error": "gmail_not_connected",
            "message": "Gmail is not connected. Please authorize Gmail access.",
            "steps": [
                "1. Go to the Integrations page",
                "2. Click 'Authorize Vault Access' on Gmail",
                "3. Allow send permissions in the Google consent screen"
            ]
        }
        
    if token == "auth0-vault-linked":
        return {
            "error": "gmail_token_not_resolved",
            "message": "Gmail integration is linked but token resolution failed. Please reconnect Gmail in Integrations."
        }
    
    to_email = params.get("to")
    subject = params.get("subject", "No Subject")
    body = params.get("body", "")
    
    if not to_email:
        return {
            "error": "missing_recipient",
            "message": "No recipient specified. Please provide a 'to' email address.",
            "example": "Send an email to john@example.com with subject 'Hello'"
        }
    
    # Build proper MIME message
    raw_message = f"To: {to_email}\nSubject: {subject}\nContent-Type: text/plain; charset=utf-8\n\n{body}"
    encoded_message = base64.urlsafe_b64encode(raw_message.encode("utf-8")).decode("utf-8")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    
    print(f"DEBUG: Sending email to {to_email}, subject: {subject}")
    response = requests.post(url, headers=headers, json={"raw": encoded_message})
    
    if response.status_code == 401:
        # Token expired
        try:
            from database.db import SessionLocal
            from database.models import Integration
            db = SessionLocal()
            db.query(Integration).filter(
                Integration.user_id == user_context["sub"],
                Integration.service == "gmail"
            ).delete()
            db.commit()
            db.close()
        except:
            pass
        return {
            "error": "gmail_token_expired",
            "message": "Your Gmail access token has expired. Please reconnect.",
            "steps": ["Go to Integrations and reconnect Gmail"]
        }
    
    if response.status_code == 403:
        return {
            "error": "gmail_send_permission_denied",
            "message": "Permission denied. Make sure you granted gmail.compose scope.",
            "details": response.text
        }
    
    if response.status_code == 200:
        result = response.json()
        return {
            "status": "success",
            "message": f"✅ Email sent successfully to {to_email}!",
            "message_id": result.get("id"),
            "thread_id": result.get("threadId")
        }
    
    return {
        "error": "gmail_send_error",
        "message": f"Failed to send email: {response.status_code}",
        "details": response.text
    }

tool_registry.register("send_gmail", send_gmail)
