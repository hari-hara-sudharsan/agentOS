"""
Browser Workflows - Complex multi-step browser automation flows
"""
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)


def execute_billing_workflow(
    provider: Dict[str, Any],
    username: str,
    password: str,
    account_number: str,
    expected_amount: Optional[float] = None,
    dry_run: bool = True,
    payment_method: str = "stored"
) -> Dict[str, Any]:
    """
    Execute complete billing payment workflow with Playwright.
    
    Steps:
    1. Navigate to provider portal
    2. Login with credentials
    3. Navigate to billing/payment section
    4. Verify account number
    5. Retrieve bill amount
    6. Initiate payment (or simulate in dry-run)
    7. Confirm payment
    8. Capture confirmation
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            selectors = provider["selectors"]
            
            # Step 1: Navigate to login page
            logger.info(f"Navigating to {provider['login_url']}")
            page.goto(provider["login_url"], wait_until="networkidle", timeout=30000)
            page.screenshot(path="screenshots/billing_1_login_page.png")
            
            # Step 2: Login
            logger.info("Logging in...")
            page.fill(selectors["username"], username)
            page.fill(selectors["password"], password)
            page.click(selectors["login_button"])
            page.wait_for_load_state("networkidle", timeout=15000)
            page.screenshot(path="screenshots/billing_2_logged_in.png")
            
            # Step 3: Verify we're logged in (check for account number or dashboard)
            try:
                # Try to find account number on page
                account_elem = page.locator(selectors["account_number"]).first
                if account_elem.is_visible(timeout=5000):
                    displayed_account = account_elem.inner_text().strip()
                    logger.info(f"Found account: {displayed_account}")
                    
                    # Verify account number matches
                    if account_number not in displayed_account and displayed_account not in account_number:
                        logger.warning(f"Account mismatch: expected {account_number}, found {displayed_account}")
            except Exception as e:
                logger.warning(f"Could not verify account number: {e}")
            
            # Step 4: Get bill amount
            logger.info("Retrieving bill amount...")
            try:
                amount_elem = page.locator(selectors["amount_display"]).first
                amount_elem.wait_for(state="visible", timeout=10000)
                amount_text = amount_elem.inner_text().strip()
                
                # Extract numeric amount (remove $, commas, etc.)
                import re
                amount_match = re.search(r'[\$]?\s*([\d,]+\.?\d*)', amount_text)
                bill_amount = float(amount_match.group(1).replace(',', '')) if amount_match else 0.0
                
                logger.info(f"Bill amount: ${bill_amount}")
                page.screenshot(path="screenshots/billing_3_bill_amount.png")
                
                # Verify expected amount if provided
                if expected_amount and abs(bill_amount - expected_amount) > 0.01:
                    return {
                        "success": False,
                        "error": f"Amount mismatch: expected ${expected_amount}, found ${bill_amount}",
                        "bill_amount": bill_amount,
                        "expected_amount": expected_amount
                    }
                
            except Exception as e:
                logger.error(f"Could not retrieve bill amount: {e}")
                bill_amount = expected_amount if expected_amount else 0.0
            
            # Step 5: Initiate payment
            if dry_run:
                logger.info("DRY RUN MODE: Simulating payment without actual submission")
                
                # Just click the pay button but don't confirm
                try:
                    pay_button = page.locator(selectors["pay_button"]).first
                    if pay_button.is_visible(timeout=5000):
                        logger.info("Pay button found (not clicking in dry-run)")
                        page.screenshot(path="screenshots/billing_4_payment_ready.png")
                except Exception as e:
                    logger.warning(f"Pay button not found: {e}")
                
                browser.close()
                
                return {
                    "success": True,
                    "message": "DRY RUN: Payment simulation completed successfully",
                    "bill_amount": bill_amount,
                    "account_number": account_number,
                    "confirmation_number": f"DRY-RUN-{int(time.time())}",
                    "timestamp": datetime.now().isoformat(),
                    "dry_run": True
                }
            
            else:
                # REAL PAYMENT MODE
                logger.info("REAL PAYMENT MODE: Submitting actual payment")
                
                # Click pay button
                pay_button = page.locator(selectors["pay_button"]).first
                pay_button.click()
                page.wait_for_load_state("networkidle", timeout=10000)
                page.screenshot(path="screenshots/billing_5_payment_initiated.png")
                
                # Wait a moment for payment form
                time.sleep(2)
                
                # Click confirm button
                confirm_button = page.locator(selectors["confirm_button"]).first
                confirm_button.wait_for(state="visible", timeout=10000)
                confirm_button.click()
                page.wait_for_load_state("networkidle", timeout=15000)
                page.screenshot(path="screenshots/billing_6_payment_confirmed.png")
                
                # Look for success message
                try:
                    success_elem = page.locator(selectors["success_message"]).first
                    success_elem.wait_for(state="visible", timeout=10000)
                    success_text = success_elem.inner_text()
                    
                    # Try to extract confirmation number
                    import re
                    conf_match = re.search(r'confirmation[:\s#]*([A-Z0-9\-]+)', success_text, re.IGNORECASE)
                    confirmation_number = conf_match.group(1) if conf_match else f"CONF-{int(time.time())}"
                    
                    logger.info(f"Payment confirmed: {confirmation_number}")
                    
                    browser.close()
                    
                    return {
                        "success": True,
                        "message": "Payment completed successfully",
                        "bill_amount": bill_amount,
                        "account_number": account_number,
                        "confirmation_number": confirmation_number,
                        "timestamp": datetime.now().isoformat(),
                        "dry_run": False
                    }
                    
                except Exception as e:
                    logger.error(f"Could not find success confirmation: {e}")
                    page.screenshot(path="screenshots/billing_error.png")
                    browser.close()
                    
                    return {
                        "success": False,
                        "error": "Payment may have been processed but confirmation not found",
                        "bill_amount": bill_amount
                    }
        
        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout during billing workflow: {e}")
            page.screenshot(path="screenshots/billing_timeout_error.png")
            browser.close()
            return {
                "success": False,
                "error": f"Timeout: {str(e)}"
            }
        
        except Exception as e:
            logger.error(f"Error during billing workflow: {e}", exc_info=True)
            try:
                page.screenshot(path="screenshots/billing_general_error.png")
            except:
                pass
            browser.close()
            return {
                "success": False,
                "error": str(e)
            }


def get_billing_info(
    provider: Dict[str, Any],
    username: str,
    password: str,
    account_number: str
) -> Dict[str, Any]:
    """
    Retrieve billing information without making payment.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            selectors = provider["selectors"]
            
            # Navigate and login
            page.goto(provider["login_url"], wait_until="networkidle", timeout=30000)
            page.fill(selectors["username"], username)
            page.fill(selectors["password"], password)
            page.click(selectors["login_button"])
            page.wait_for_load_state("networkidle", timeout=15000)
            
            # Get account info
            account_elem = page.locator(selectors["account_number"]).first
            displayed_account = account_elem.inner_text().strip() if account_elem.is_visible(timeout=5000) else account_number
            
            # Get bill amount
            amount_elem = page.locator(selectors["amount_display"]).first
            amount_elem.wait_for(state="visible", timeout=10000)
            amount_text = amount_elem.inner_text().strip()
            
            import re
            amount_match = re.search(r'[\$]?\s*([\d,]+\.?\d*)', amount_text)
            bill_amount = float(amount_match.group(1).replace(',', '')) if amount_match else 0.0
            
            page.screenshot(path="screenshots/billing_info.png")
            browser.close()
            
            return {
                "success": True,
                "bill_amount": bill_amount,
                "account_number": displayed_account,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error retrieving billing info: {e}", exc_info=True)
            try:
                page.screenshot(path="screenshots/billing_info_error.png")
            except:
                pass
            browser.close()
            return {
                "success": False,
                "error": str(e)
            }


def electricity_bill_workflow() -> Dict[str, Any]:
    """
    Legacy wrapper for electricity bill workflow.
    This is a simple demo that returns mock data.
    For real billing, use execute_billing_workflow() with proper credentials.
    """
    logger.info("Executing electricity bill workflow (demo mode)")
    
    return {
        "success": True,
        "message": "Electricity bill workflow executed (demo mode)",
        "provider": "Demo Electric Company",
        "account_number": "DEMO-12345",
        "bill_amount": 127.50,
        "due_date": "2024-04-15",
        "status": "pending",
        "dry_run": True,
        "note": "This is a demo. Use execute_billing_workflow() for real payments."
    }
