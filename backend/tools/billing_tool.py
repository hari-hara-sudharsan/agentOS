"""
Billing Tool - Automates electricity bill payment with multiple provider support
Includes dry-run mode for safe testing without actual payment submission
"""
from registry.tool_registry import tool_registry
from security.auth0_client import check_mfa_and_consent
from browser.playwright_runner import run_browser_task
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


# Supported electricity providers with their portal configurations
SUPPORTED_PROVIDERS = {
    "demo_electric": {
        "name": "Demo Electric Company",
        "url": "https://demo-electric-portal.example.com",
        "login_url": "https://demo-electric-portal.example.com/login",
        "selectors": {
            "username": "#username",
            "password": "#password",
            "login_button": "button[type='submit']",
            "account_number": "#account-number",
            "amount_display": ".bill-amount",
            "pay_button": "#pay-now-button",
            "confirm_button": "#confirm-payment",
            "success_message": ".payment-success"
        }
    },
    "test_power_co": {
        "name": "Test Power Co",
        "url": "https://testpower.example.com",
        "login_url": "https://testpower.example.com/account/login",
        "selectors": {
            "username": "input[name='email']",
            "password": "input[name='password']",
            "login_button": "#login-btn",
            "account_number": "#acct-num",
            "amount_display": "#current-balance",
            "pay_button": ".btn-pay",
            "confirm_button": ".btn-confirm",
            "success_message": "#payment-confirmation"
        }
    },
    "sample_utilities": {
        "name": "Sample Utilities Inc",
        "url": "https://billing.sampleutilities.example.com",
        "login_url": "https://billing.sampleutilities.example.com/signin",
        "selectors": {
            "username": "input#user-email",
            "password": "input#user-password",
            "login_button": "button.submit-login",
            "account_number": "span.account-id",
            "amount_display": "div.amount-due",
            "pay_button": "button#make-payment",
            "confirm_button": "button#finalize-payment",
            "success_message": "div.success-alert"
        }
    },
    "mock_energy": {
        "name": "Mock Energy Services",
        "url": "https://portal.mockenergy.example.com",
        "login_url": "https://portal.mockenergy.example.com/auth",
        "selectors": {
            "username": "[data-testid='username-input']",
            "password": "[data-testid='password-input']",
            "login_button": "[data-testid='login-submit']",
            "account_number": "[data-testid='account-num']",
            "amount_display": "[data-testid='balance-amount']",
            "pay_button": "[data-testid='pay-btn']",
            "confirm_button": "[data-testid='confirm-btn']",
            "success_message": "[data-testid='success-msg']"
        }
    },
    "demo_grid": {
        "name": "Demo Grid Corporation",
        "url": "https://my.demogrid.example.com",
        "login_url": "https://my.demogrid.example.com/customer-login",
        "selectors": {
            "username": "#customerEmail",
            "password": "#customerPassword",
            "login_button": ".login-form button[type='submit']",
            "account_number": ".account-info .account-num",
            "amount_display": ".billing-summary .total-due",
            "pay_button": "button.initiate-payment",
            "confirm_button": "button.complete-payment",
            "success_message": ".alert-success"
        }
    }
}


def pay_electricity_bill(user_context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pay electricity bill for a specified provider and account.
    
    This tool:
    1. Logs into the electricity provider's portal
    2. Navigates to the billing section
    3. Retrieves current bill amount
    4. Initiates payment (or simulates in dry-run mode)
    5. Confirms payment
    
    Parameters:
        - account_number: Account number with the electricity provider
        - provider: Provider code (demo_electric, test_power_co, sample_utilities, mock_energy, demo_grid)
        - amount: (optional) Expected bill amount for verification
        - dry_run: (optional) If True, simulates payment without actually submitting. Default: True
        - username: (optional) Provider portal username/email
        - password: (optional) Provider portal password
        - payment_method: (optional) Payment method ID/last 4 digits. Default: "stored"
    
    Returns:
        Dict with payment status, confirmation number, and transaction details
    """
    # High-stakes action - require MFA/consent
    check_mfa_and_consent(user_context, params, tool="pay_electricity_bill")
    
    account_number = params.get("account_number")
    provider_code = params.get("provider", "demo_electric").lower()
    expected_amount = params.get("amount")
    dry_run = params.get("dry_run", True)  # Default to dry-run for safety
    username = params.get("username")
    password = params.get("password")
    payment_method = params.get("payment_method", "stored")
    
    # Validate provider
    if provider_code not in SUPPORTED_PROVIDERS:
        return {
            "success": False,
            "error": f"Unsupported provider: {provider_code}",
            "supported_providers": list(SUPPORTED_PROVIDERS.keys())
        }
    
    provider = SUPPORTED_PROVIDERS[provider_code]
    
    # Get credentials from database if not provided
    if not username or not password:
        from database.db import SessionLocal
        from database.models import Integration
        
        db = SessionLocal()
        try:
            integration = db.query(Integration).filter(
                Integration.user_id == user_context["sub"],
                Integration.service == f"billing_{provider_code}"
            ).first()
            
            if integration and integration.extra_data:
                import json
                try:
                    extra = json.loads(integration.extra_data)
                    username = extra.get("username", username)
                    password = extra.get("password", password)
                    if not account_number:
                        account_number = extra.get("account_number")
                except json.JSONDecodeError:
                    pass
        finally:
            db.close()
    
    if not username or not password:
        return {
            "success": False,
            "error": "Missing credentials. Please provide username and password or configure integration.",
            "provider": provider["name"]
        }
    
    if not account_number:
        return {
            "success": False,
            "error": "Account number is required",
            "provider": provider["name"]
        }
    
    logger.info(f"Starting bill payment for {provider['name']} - Account: {account_number} (Dry-run: {dry_run})")
    
    try:
        # Execute the billing workflow
        from browser.workflows import execute_billing_workflow
        
        result = execute_billing_workflow(
            provider=provider,
            username=username,
            password=password,
            account_number=account_number,
            expected_amount=expected_amount,
            dry_run=dry_run,
            payment_method=payment_method
        )
        
        # Add metadata
        result["provider"] = provider["name"]
        result["provider_code"] = provider_code
        result["account_number"] = account_number
        result["dry_run"] = dry_run
        result["timestamp"] = datetime.now().isoformat()
        
        if dry_run and result.get("success"):
            result["message"] = "DRY RUN: Payment simulation completed successfully. No actual payment was made."
        
        logger.info(f"Bill payment result: {result.get('success')} - {result.get('message', 'No message')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Bill payment failed: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "provider": provider["name"],
            "account_number": account_number,
            "dry_run": dry_run
        }


def get_bill_amount(user_context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve current electricity bill amount without making payment.
    
    Parameters:
        - account_number: Account number with the electricity provider
        - provider: Provider code
        - username: (optional) Provider portal username/email
        - password: (optional) Provider portal password
    
    Returns:
        Dict with current bill amount, due date, and account details
    """
    # Lower stakes - just reading data
    check_mfa_and_consent(user_context, params, tool="get_bill_amount")
    
    account_number = params.get("account_number")
    provider_code = params.get("provider", "demo_electric").lower()
    username = params.get("username")
    password = params.get("password")
    
    if provider_code not in SUPPORTED_PROVIDERS:
        return {
            "success": False,
            "error": f"Unsupported provider: {provider_code}",
            "supported_providers": list(SUPPORTED_PROVIDERS.keys())
        }
    
    provider = SUPPORTED_PROVIDERS[provider_code]
    
    # Get credentials from database if not provided
    if not username or not password:
        from database.db import SessionLocal
        from database.models import Integration
        
        db = SessionLocal()
        try:
            integration = db.query(Integration).filter(
                Integration.user_id == user_context["sub"],
                Integration.service == f"billing_{provider_code}"
            ).first()
            
            if integration and integration.extra_data:
                import json
                try:
                    extra = json.loads(integration.extra_data)
                    username = extra.get("username", username)
                    password = extra.get("password", password)
                    if not account_number:
                        account_number = extra.get("account_number")
                except json.JSONDecodeError:
                    pass
        finally:
            db.close()
    
    if not username or not password:
        return {
            "success": False,
            "error": "Missing credentials",
            "provider": provider["name"]
        }
    
    try:
        from browser.workflows import get_billing_info
        
        result = get_billing_info(
            provider=provider,
            username=username,
            password=password,
            account_number=account_number
        )
        
        result["provider"] = provider["name"]
        result["provider_code"] = provider_code
        result["account_number"] = account_number
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to retrieve bill amount: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "provider": provider["name"]
        }


def list_billing_providers() -> Dict[str, Any]:
    """
    List all supported electricity billing providers.
    
    Returns:
        Dict with list of supported providers and their details
    """
    providers_list = []
    for code, info in SUPPORTED_PROVIDERS.items():
        providers_list.append({
            "code": code,
            "name": info["name"],
            "url": info["url"]
        })
    
    return {
        "success": True,
        "providers": providers_list,
        "count": len(providers_list)
    }


# Register the tools
tool_registry.register("pay_electricity_bill", pay_electricity_bill)
tool_registry.register("get_bill_amount", get_bill_amount)
tool_registry.register("list_billing_providers", list_billing_providers)
