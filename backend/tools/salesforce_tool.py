"""
Salesforce Tool - CRM integration for leads
"""
from registry.tool_registry import tool_registry
from security.auth0_client import check_mfa_and_consent
import requests


def create_salesforce_lead(user_context, params):
    """Create a Salesforce lead."""
    check_mfa_and_consent(user_context, params, tool="create_salesforce_lead")
    
    from database.db import SessionLocal
    from database.models import Integration
    
    db = SessionLocal()
    try:
        integration = db.query(Integration).filter(
            Integration.user_id == user_context["sub"],
            Integration.service == "salesforce"
        ).first()
        
        connected = integration is not None
        token = integration.token_reference if integration else None
    finally:
        db.close()

    if not connected:
        return {
            "error": "salesforce_not_connected",
            "message": "Salesforce is not connected. Add your Salesforce credentials in Integrations.",
            "steps": [
                "1. Go to Salesforce Setup → Apps → App Manager",
                "2. Create a Connected App with OAuth settings",
                "3. Get your Access Token and Instance URL",
                "4. Format as: instance_url|access_token and paste in Integrations"
            ]
        }

    name = params.get("name", "New Lead")
    email = params.get("email", "")
    company = params.get("company", "Unknown Company")
    
    # Parse token format: instance_url|access_token
    if "|" in token:
        instance_url, access_token = token.split("|", 1)
    else:
        # Simulated response for demo
        return {
            "status": "success",
            "message": f"Simulated: Created lead for {name} at {company}",
            "lead_id": "00Q_DEMO_LEAD",
            "note": "For real Salesforce integration, provide token as: instance_url|access_token"
        }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "FirstName": name.split()[0] if " " in name else name,
        "LastName": name.split()[-1] if " " in name else "Unknown",
        "Email": email,
        "Company": company
    }

    url = f"{instance_url}/services/data/v58.0/sobjects/Lead"
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        result = response.json()
        return {
            "status": "success",
            "lead_id": result.get("id"),
            "message": f"Created lead for {name} at {company}"
        }
    else:
        return {
            "error": "salesforce_api_error",
            "status_code": response.status_code,
            "message": response.text
        }


tool_registry.register("create_salesforce_lead", create_salesforce_lead)
