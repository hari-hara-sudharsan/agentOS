"""
Microsoft/Azure Tool - Simulated Azure operations
Note: Real Azure integration requires Azure AD setup in Auth0.
This provides stub responses for demo purposes.
"""
from registry.tool_registry import tool_registry
from security.auth0_client import check_mfa_and_consent


def create_azure_resource(user_context, params):
    """Create an Azure resource (simulated for demo)."""
    check_mfa_and_consent(user_context, params, tool="create_azure_resource")
    
    from database.db import SessionLocal
    from database.models import Integration
    
    db = SessionLocal()
    try:
        integration = db.query(Integration).filter(
            Integration.user_id == user_context["sub"],
            Integration.service == "microsoft_azure"
        ).first()
        
        connected = integration is not None
    finally:
        db.close()

    if not connected:
        return {
            "error": "azure_not_connected",
            "message": "Microsoft Azure is not connected. Add your Azure credentials in the Integrations page.",
            "steps": [
                "1. Go to Azure Portal → App registrations → Create new app",
                "2. Configure redirect URI and permissions",
                "3. Copy Application (client) ID and add to Integrations page"
            ]
        }

    resource_group = params.get("resource_group", "default-rg")
    resource_type = params.get("resource_type", "vm")
    config = params.get("config", {})

    # Simulated response for demo
    return {
        "status": "success",
        "message": f"Successfully created {resource_type} in resource group '{resource_group}'",
        "resource_id": f"/subscriptions/demo/resourceGroups/{resource_group}/{resource_type}/demo-resource",
        "note": "This is a simulated response. Real Azure integration requires Azure AD OAuth setup."
    }


def list_azure_resources(user_context, params):
    """List Azure resources (simulated for demo)."""
    from database.db import SessionLocal
    from database.models import Integration
    
    db = SessionLocal()
    try:
        integration = db.query(Integration).filter(
            Integration.user_id == user_context["sub"],
            Integration.service == "microsoft_azure"
        ).first()
        
        connected = integration is not None
    finally:
        db.close()

    if not connected:
        return {"error": "azure_not_connected"}

    # Simulated response
    return {
        "status": "success",
        "resources": [
            {"name": "demo-vm-1", "type": "VirtualMachine", "status": "Running"},
            {"name": "demo-storage", "type": "StorageAccount", "status": "Active"},
            {"name": "demo-webapp", "type": "WebApp", "status": "Running"}
        ],
        "note": "Simulated response for demo purposes"
    }


tool_registry.register("create_azure_resource", create_azure_resource)
tool_registry.register("list_azure_resources", list_azure_resources)
