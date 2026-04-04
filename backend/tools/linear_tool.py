"""
Linear Tool - Issue tracking integration
"""
from registry.tool_registry import tool_registry
from security.auth0_client import check_mfa_and_consent
import requests


def create_linear_issue(user_context, params):
    """Create a Linear issue."""
    check_mfa_and_consent(user_context, params, tool="create_linear_issue")
    
    from database.db import SessionLocal
    from database.models import Integration
    
    db = SessionLocal()
    try:
        integration = db.query(Integration).filter(
            Integration.user_id == user_context["sub"],
            Integration.service == "linear"
        ).first()
        
        token = integration.token_reference if integration else None
    finally:
        db.close()

    if not token:
        return {
            "error": "linear_not_connected",
            "message": "Linear is not connected. Go to Integrations page and add your Linear API key.",
            "steps": [
                "1. Go to linear.app → Settings → API → Personal API keys",
                "2. Create a new key",
                "3. Copy and paste it in the Integrations page"
            ]
        }

    title = params.get("title", "New Issue")
    description = params.get("description", "")
    team_id = params.get("team_id")

    # Linear uses GraphQL API
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    # First, get teams if no team_id provided
    if not team_id:
        query = """
        query {
            teams {
                nodes {
                    id
                    name
                }
            }
        }
        """
        response = requests.post(
            "https://api.linear.app/graphql",
            headers=headers,
            json={"query": query}
        )
        
        if response.status_code == 200:
            data = response.json()
            teams = data.get("data", {}).get("teams", {}).get("nodes", [])
            if teams:
                team_id = teams[0]["id"]
            else:
                return {"error": "No teams found in your Linear workspace"}
        else:
            return {"error": "linear_api_error", "message": response.text}

    # Create issue
    mutation = """
    mutation CreateIssue($input: IssueCreateInput!) {
        issueCreate(input: $input) {
            success
            issue {
                id
                identifier
                title
                url
            }
        }
    }
    """
    
    variables = {
        "input": {
            "teamId": team_id,
            "title": title,
            "description": description
        }
    }

    response = requests.post(
        "https://api.linear.app/graphql",
        headers=headers,
        json={"query": mutation, "variables": variables}
    )
    
    if response.status_code == 200:
        data = response.json()
        issue_data = data.get("data", {}).get("issueCreate", {})
        if issue_data.get("success"):
            issue = issue_data.get("issue", {})
            return {
                "status": "success",
                "identifier": issue.get("identifier"),
                "url": issue.get("url"),
                "message": f"Created issue {issue.get('identifier')}: {title}"
            }
        else:
            return {"error": "linear_create_failed", "data": data}
    else:
        return {"error": "linear_api_error", "message": response.text}


tool_registry.register("create_linear_issue", create_linear_issue)
