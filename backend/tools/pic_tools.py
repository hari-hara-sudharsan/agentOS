from registry.tool_registry import tool_registry
from integrations.integration_service import get_integration_token
import requests

from security.auth0_client import check_mfa_and_consent

def create_image(user_context, params, memory=None):
    check_mfa_and_consent(user_context, params, tool="create_image")

    token = get_integration_token(user_context, "pic_tools")
    if not token:
        return {"error": "pic_tools not connected (provide API key via Integrations)."}

    prompt = params.get("prompt") or params.get("description")
    if not prompt:
        return {"error": "Image prompt is required. Use 'prompt' parameter."}

    # Simulated or fallback response
    if token == "auth0-vault-linked":
        return {
            "ok": True,
            "image_url": "https://placekitten.com/1024/1024",
            "message": "Created a placeholder image from Pic Tools mock environment."
        }

    try:
        # Replace this with a real Pic Tools API call path if available.
        response = requests.post(
            "https://api.pictools.io/v1/image/create",
            json={"prompt": prompt},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=15
        )
        if response.status_code == 200:
            return response.json()
        return {"error": f"Pic Tools API failed ({response.status_code}): {response.text}"}
    except Exception as exc:
        return {"error": f"Pic Tools request error: {str(exc)}"}


tool_registry.register("create_image", create_image)
