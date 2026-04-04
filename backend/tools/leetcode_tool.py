"""
LeetCode Tool - Automates daily problem submission on LeetCode
"""
from registry.tool_registry import tool_registry
from security.auth0_client import check_mfa_and_consent
from browser.playwright_runner import run_browser_task
import logging

logger = logging.getLogger(__name__)


def complete_leetcode_daily(user_context, params):
    """
    Complete today's LeetCode daily problem by submitting a solution.
    
    This tool:
    1. Opens LeetCode
    2. Logs in with stored credentials
    3. Navigates to the daily challenge
    4. Submits the provided solution code
    
    Parameters:
        - solution_code: (optional) The code to submit. If not provided, will use a template.
        - language: (optional) Programming language (python3, java, cpp, javascript). Default: python3
        - username: LeetCode username/email
        - password: LeetCode password
    """
    # This is a high-stakes action - require MFA/consent
    check_mfa_and_consent(user_context, params, tool="complete_leetcode_daily")
    
    username = params.get("username")
    password = params.get("password")
    solution_code = params.get("solution_code", "")
    language = params.get("language", "python3")
    
    if not username or not password:
        # Try to get from database integration
        from database.db import SessionLocal
        from database.models import Integration
        
        db = SessionLocal()
        try:
            integration = db.query(Integration).filter(
                Integration.user_id == user_context["sub"],
                Integration.service == "leetcode"
            ).first()
            
            if integration and integration.extra_data:
                import json
                try:
                    extra = json.loads(integration.extra_data) if isinstance(integration.extra_data, str) else integration.extra_data
                    username = username or extra.get("username")
                    password = password or integration.token_reference
                except:
                    pass
        finally:
            db.close()
    
    if not username or not password:
        return {
            "error": "leetcode_not_connected",
            "message": "LeetCode credentials not found. Please provide username and password, or connect LeetCode in Integrations.",
            "steps": [
                "1. Go to the Integrations page",
                "2. Add LeetCode with your username and password",
                "3. Or provide username/password in your request"
            ]
        }
    
    logger.info(f"Starting LeetCode daily problem completion for user {username}")
    
    # Execute the browser workflow
    result = run_leetcode_workflow(username, password, solution_code, language)
    
    return result


def run_leetcode_workflow(username, password, solution_code, language):
    """
    Execute the LeetCode workflow using Playwright.
    Returns the result of the submission.
    """
    from playwright.sync_api import sync_playwright
    import time
    
    try:
        with sync_playwright() as p:
            # Use headless=False for debugging, True for production
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            
            try:
                # Step 1: Navigate to LeetCode login
                logger.info("Navigating to LeetCode...")
                page.goto("https://leetcode.com/accounts/login/", timeout=30000)
                page.wait_for_load_state("domcontentloaded")
                time.sleep(2)
                
                # Step 2: Login
                logger.info("Logging in...")
                
                # Try multiple selector strategies for username
                username_selectors = [
                    'input[name="login"]',
                    'input[id="id_login"]', 
                    'input[placeholder*="Username"]',
                    'input[placeholder*="email"]',
                    'input[type="text"]'
                ]
                
                username_filled = False
                for sel in username_selectors:
                    try:
                        if page.locator(sel).first.is_visible(timeout=2000):
                            page.fill(sel, username, timeout=3000)
                            username_filled = True
                            break
                    except:
                        continue
                
                if not username_filled:
                    return {"error": "login_failed", "message": "Could not find username input field"}
                
                # Fill password
                password_selectors = [
                    'input[name="password"]',
                    'input[id="id_password"]',
                    'input[type="password"]'
                ]
                
                password_filled = False
                for sel in password_selectors:
                    try:
                        if page.locator(sel).first.is_visible(timeout=2000):
                            page.fill(sel, password, timeout=3000)
                            password_filled = True
                            break
                    except:
                        continue
                
                if not password_filled:
                    return {"error": "login_failed", "message": "Could not find password input field"}
                
                # Click login button
                login_selectors = [
                    'button[type="submit"]',
                    'button:has-text("Sign In")',
                    'button:has-text("Login")',
                    '#signin_btn'
                ]
                
                for sel in login_selectors:
                    try:
                        if page.locator(sel).first.is_visible(timeout=2000):
                            page.click(sel, timeout=3000)
                            break
                    except:
                        continue
                
                # Wait for login to complete
                time.sleep(5)
                
                # Check if login successful
                if "login" in page.url.lower():
                    # Still on login page - might have error
                    error_text = ""
                    try:
                        error_elem = page.locator('.error, .alert-danger, [class*="error"]').first
                        if error_elem.is_visible(timeout=2000):
                            error_text = error_elem.inner_text()
                    except:
                        pass
                    
                    return {
                        "error": "login_failed",
                        "message": f"Login failed. {error_text}".strip(),
                        "hint": "Check your username/password or try logging in manually first"
                    }
                
                logger.info("Login successful! Navigating to daily problem...")
                
                # Step 3: Navigate to daily challenge
                page.goto("https://leetcode.com/problemset/", timeout=30000)
                page.wait_for_load_state("domcontentloaded")
                time.sleep(3)
                
                # Look for the daily challenge - it's usually marked with a calendar icon or "Daily Challenge"
                daily_selectors = [
                    'a[href*="/problems/"][class*="daily"]',
                    '[data-testid="daily-challenge"]',
                    'a:has-text("Daily Challenge")',
                    '.daily-challenge-link'
                ]
                
                # Try to find daily challenge on main page
                daily_found = False
                for sel in daily_selectors:
                    try:
                        if page.locator(sel).first.is_visible(timeout=3000):
                            page.click(sel)
                            daily_found = True
                            break
                    except:
                        continue
                
                if not daily_found:
                    # Navigate directly to daily coding challenge page
                    page.goto("https://leetcode.com/problemset/all/?page=1&sorting=daily", timeout=30000)
                    time.sleep(3)
                    
                    # Try to click the first problem (which should be today's daily)
                    try:
                        first_problem = page.locator('a[href*="/problems/"]').first
                        if first_problem.is_visible(timeout=3000):
                            first_problem.click()
                            daily_found = True
                    except:
                        pass
                
                if not daily_found:
                    # Last resort: go to leetcode.com and look for daily challenge banner
                    page.goto("https://leetcode.com/", timeout=30000)
                    time.sleep(3)
                    
                    try:
                        daily_banner = page.locator('[class*="daily"], [class*="Daily"]').first
                        if daily_banner.is_visible(timeout=3000):
                            daily_banner.click()
                            daily_found = True
                    except:
                        pass
                
                time.sleep(3)
                page.wait_for_load_state("domcontentloaded")
                
                # Get problem title
                problem_title = ""
                try:
                    title_elem = page.locator('h4[data-cy="question-title"], .question-title, h3').first
                    if title_elem.is_visible(timeout=3000):
                        problem_title = title_elem.inner_text()
                except:
                    problem_title = page.url.split("/problems/")[-1].rstrip("/") if "/problems/" in page.url else "Unknown"
                
                logger.info(f"Found problem: {problem_title}")
                
                # Step 4: Submit solution (if provided)
                if solution_code:
                    logger.info("Submitting solution...")
                    
                    # Select language
                    try:
                        lang_dropdown = page.locator('button[class*="lang"], [data-cy="lang-select"]').first
                        if lang_dropdown.is_visible(timeout=3000):
                            lang_dropdown.click()
                            time.sleep(1)
                            
                            lang_option = page.locator(f'div:has-text("{language}")').first
                            if lang_option.is_visible(timeout=2000):
                                lang_option.click()
                                time.sleep(1)
                    except:
                        logger.warning("Could not select language, using default")
                    
                    # Find and clear the code editor
                    try:
                        # Monaco editor textarea
                        editor = page.locator('.monaco-editor textarea, .CodeMirror textarea').first
                        if editor.is_visible(timeout=3000):
                            # Clear existing code
                            page.keyboard.press("Control+A")
                            time.sleep(0.5)
                            
                            # Type new code
                            page.keyboard.type(solution_code, delay=10)
                            time.sleep(1)
                    except Exception as e:
                        logger.warning(f"Could not enter code in editor: {e}")
                        return {
                            "status": "partial_success",
                            "problem_title": problem_title,
                            "message": "Navigated to problem but could not enter code. Please submit manually.",
                            "url": page.url
                        }
                    
                    # Click Submit button
                    try:
                        submit_btn = page.locator('button:has-text("Submit"), [data-cy="submit-code-btn"]').first
                        if submit_btn.is_visible(timeout=3000):
                            submit_btn.click()
                            logger.info("Solution submitted!")
                            time.sleep(5)  # Wait for result
                            
                            # Check submission result
                            result_text = ""
                            try:
                                result_elem = page.locator('[class*="result"], [class*="accepted"], [class*="wrong"]').first
                                if result_elem.is_visible(timeout=10000):
                                    result_text = result_elem.inner_text()
                            except:
                                result_text = "Submission sent (check LeetCode for result)"
                            
                            return {
                                "status": "submitted",
                                "problem_title": problem_title,
                                "result": result_text,
                                "url": page.url,
                                "message": f"Successfully submitted solution for '{problem_title}'"
                            }
                    except:
                        pass
                
                # No solution provided - just return problem info
                return {
                    "status": "navigated",
                    "problem_title": problem_title,
                    "url": page.url,
                    "message": f"Navigated to today's problem: {problem_title}. No solution code provided - please provide solution_code to auto-submit."
                }
                
            except Exception as e:
                logger.error(f"LeetCode workflow error: {e}")
                
                # Take screenshot for debugging
                try:
                    screenshot_path = f"leetcode_error_{int(time.time())}.png"
                    page.screenshot(path=screenshot_path)
                except:
                    screenshot_path = None
                
                return {
                    "error": "workflow_error",
                    "message": str(e),
                    "screenshot": screenshot_path
                }
            finally:
                browser.close()
                
    except Exception as e:
        return {
            "error": "playwright_error",
            "message": f"Browser automation error: {str(e)}",
            "hint": "Make sure Playwright is installed: pip install playwright && playwright install chromium"
        }


def get_leetcode_daily_problem(user_context, params):
    """
    Get information about today's LeetCode daily problem without submitting.
    Useful for checking what the problem is before deciding to submit.
    """
    from browser.playwright_runner import run_browser_task
    
    # Use browser search to find today's LeetCode daily
    result = run_browser_task("browser_search", {
        "query": "LeetCode daily challenge today problem"
    })
    
    return {
        "status": "search_complete",
        "daily_problem_info": result.get("text", ""),
        "message": "Use 'complete_leetcode_daily' with solution_code to submit"
    }


# Register tools
tool_registry.register("complete_leetcode_daily", complete_leetcode_daily)
tool_registry.register("get_leetcode_daily_problem", get_leetcode_daily_problem)
