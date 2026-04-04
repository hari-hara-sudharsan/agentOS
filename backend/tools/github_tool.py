"""
GitHub Tool - Creates issues via GitHub Personal Access Token
"""
from registry.tool_registry import tool_registry
from security.auth0_client import check_mfa_and_consent
import requests


def create_github_issue(user_context, params):
    """Create a GitHub issue in a repository."""
    check_mfa_and_consent(user_context, params, tool="create_github_issue")
    
    # Get token from database
    from database.db import SessionLocal
    from database.models import Integration
    
    db = SessionLocal()
    try:
        integration = db.query(Integration).filter(
            Integration.user_id == user_context["sub"],
            Integration.service == "github"
        ).first()
        
        token = integration.token_reference if integration else None
    finally:
        db.close()

    if not token:
        return {
            "error": "github_not_connected",
            "message": "GitHub is not connected. Go to Integrations page and add your GitHub Personal Access Token.",
            "steps": [
                "1. Go to github.com → Settings → Developer settings → Personal access tokens",
                "2. Generate new token (classic) with 'repo' scope",
                "3. Copy the token and paste it in the Integrations page"
            ]
        }

    repo = params.get("repo")
    title = params.get("title", "New Issue")
    body = params.get("body", "")
    
    if not repo:
        return {"error": "Missing 'repo' parameter. Format: owner/repo-name"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    payload = {
        "title": title,
        "body": body
    }

    url = f"https://api.github.com/repos/{repo}/issues"
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    if response.status_code == 201:
        return {
            "status": "success",
            "issue_number": result.get("number"),
            "url": result.get("html_url"),
            "message": f"Created issue #{result.get('number')} in {repo}"
        }
    else:
        return {
            "error": "github_api_error",
            "status_code": response.status_code,
            "message": result.get("message", str(result))
        }


def list_github_repos(user_context, params):
    """List GitHub repositories for the authenticated user."""
    from database.db import SessionLocal
    from database.models import Integration
    
    db = SessionLocal()
    try:
        integration = db.query(Integration).filter(
            Integration.user_id == user_context["sub"],
            Integration.service == "github"
        ).first()
        
        token = integration.token_reference if integration else None
    finally:
        db.close()

    if not token:
        return {"error": "github_not_connected"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    url = "https://api.github.com/user/repos?per_page=10&sort=updated"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        repos = response.json()
        return {
            "status": "success",
            "repos": [{"name": r["full_name"], "url": r["html_url"]} for r in repos[:10]]
        }
    else:
        return {"error": "github_api_error", "message": response.text}


tool_registry.register("create_github_issue", create_github_issue)
tool_registry.register("list_github_repos", list_github_repos)
