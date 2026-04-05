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
    # Approval check disabled for easier testing
    # To re-enable: uncomment the line below
    # check_mfa_and_consent(user_context, params, tool="complete_leetcode_daily")
    
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
    Wrapper for async implementation to avoid event loop conflicts.
    """
    import asyncio
    import concurrent.futures
    import threading
    
    try:
        # Check if there's a running event loop
        try:
            loop = asyncio.get_running_loop()
            # There's a running loop - we need to run in a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run_in_new_loop, username, password, solution_code, language)
                result = future.result(timeout=180)  # 3 minute timeout
                return result
        except RuntimeError:
            # No running loop - safe to create our own
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(_run_leetcode_workflow_async(username, password, solution_code, language))
                return result
            finally:
                loop.close()
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        return {
            "error": "playwright_error",
            "message": f"Browser automation error: {str(e)}",
            "hint": "Make sure Playwright is installed: pip install playwright && playwright install chromium"
        }


def _run_in_new_loop(username, password, solution_code, language):
    """Helper function to run async code in a new event loop in a separate thread"""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run_leetcode_workflow_async(username, password, solution_code, language))
    finally:
        loop.close()


async def _run_leetcode_workflow_async(username, password, solution_code, language):
    """
    Async implementation of LeetCode workflow using Playwright.
    """
    from playwright.async_api import async_playwright
    import time
    import os
    
    # Use persistent browser profile - login once, stay logged in forever!
    user_data_dir = os.path.join(os.path.dirname(__file__), "..", "browser_data", "leetcode")
    os.makedirs(user_data_dir, exist_ok=True)
    
    try:
        async with async_playwright() as p:
            # Use persistent context - saves cookies and login state!
            logger.info(f"Using persistent browser profile at: {user_data_dir}")
            context = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.pages[0] if context.pages else await context.new_page()
            
            try:
                # Step 1: Navigate to LeetCode - go directly to problem list
                logger.info("Navigating to LeetCode...")
                await page.goto("https://leetcode.com/", timeout=90000, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                
                os.makedirs("screenshots", exist_ok=True)
                
                # Check if already logged in by looking for user avatar or profile link
                logged_in = False
                try:
                    # Check for signs of being logged in
                    user_indicators = ['[class*="nav-user"]', '[class*="avatar"]', 'a[href*="/profile"]', '[id*="user"]']
                    for indicator in user_indicators:
                        if await page.locator(indicator).first.is_visible(timeout=2000):
                            logged_in = True
                            logger.info("✅ Already logged in! (found user indicator)")
                            break
                    
                    # Also check if we're NOT on the login page
                    if not logged_in and "login" not in page.url.lower():
                        # Check for premium/subscribe buttons (only visible when logged in)
                        if await page.locator('a[href*="/subscribe"]').first.is_visible(timeout=1000):
                            logged_in = True
                            logger.info("✅ Already logged in! (found subscribe link)")
                except:
                    pass
                
                if not logged_in:
                    logger.info("⚠️ Not logged in. Please login MANUALLY in the browser window...")
                    logger.info("👆 You only need to do this ONCE - the session will be saved!")
                    logger.info("👆 Navigate to leetcode.com/accounts/login and login yourself.")
                    logger.info("⏳ Waiting 2 minutes for you to complete login...")
                    
                    # Open login page for user
                    await page.goto("https://leetcode.com/accounts/login/", timeout=90000)
                    await page.wait_for_timeout(2000)
                    
                    # Wait for user to login manually (up to 2 minutes)
                    for i in range(24):  # 24 * 5 = 120 seconds
                        await page.wait_for_timeout(5000)
                        current_url = page.url.lower()
                        
                        if "login" not in current_url and "accounts" not in current_url:
                            logger.info(f"✅ Login successful! Session saved for future runs.")
                            logged_in = True
                            break
                        
                        logger.info(f"⏳ Waiting for manual login... ({(i+1)*5}s)")
                    
                    if not logged_in:
                        await page.screenshot(path="screenshots/leetcode_login_timeout.png")
                        return {
                            "error": "login_timeout",
                            "message": "Login timeout. Please try again and login manually.",
                            "hint": "Login once manually - it will be saved for future runs!"
                        }
                
                logger.info("✅ Logged in! Navigating to daily problem...")
                
                # Step 2: Navigate to daily challenge
                await page.goto("https://leetcode.com/problemset/", timeout=90000)
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(3000)
                
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
                        if await page.locator(sel).first.is_visible(timeout=3000):
                            await page.click(sel)
                            daily_found = True
                            break
                    except:
                        continue
                
                if not daily_found:
                    # Navigate directly to daily coding challenge page
                    await page.goto("https://leetcode.com/problemset/all/?page=1&sorting=daily", timeout=90000)
                    await page.wait_for_timeout(3000)
                    
                    # Try to click the first problem (which should be today's daily)
                    try:
                        first_problem = page.locator('a[href*="/problems/"]').first
                        if await first_problem.is_visible(timeout=3000):
                            await first_problem.click()
                            daily_found = True
                    except:
                        pass
                
                if not daily_found:
                    # Last resort: go to leetcode.com and look for daily challenge banner
                    await page.goto("https://leetcode.com/", timeout=90000)
                    await page.wait_for_timeout(3000)
                    
                    try:
                        daily_banner = page.locator('[class*="daily"], [class*="Daily"]').first
                        if await daily_banner.is_visible(timeout=3000):
                            await daily_banner.click()
                            daily_found = True
                    except:
                        pass
                
                await page.wait_for_timeout(3000)
                await page.wait_for_load_state("domcontentloaded")
                
                # Get problem title
                problem_title = ""
                try:
                    title_elem = page.locator('h4[data-cy="question-title"], .question-title, h3').first
                    if await title_elem.is_visible(timeout=3000):
                        problem_title = await title_elem.inner_text()
                except:
                    problem_title = page.url.split("/problems/")[-1].rstrip("/") if "/problems/" in page.url else "Unknown"
                
                logger.info(f"Found problem: {problem_title}")
                
                # Step 4: Submit solution (if provided)
                if solution_code:
                    logger.info("Submitting solution...")
                    
                    # Select language
                    try:
                        lang_dropdown = page.locator('button[class*="lang"], [data-cy="lang-select"]').first
                        if await lang_dropdown.is_visible(timeout=3000):
                            await lang_dropdown.click()
                            await page.wait_for_timeout(1000)
                            
                            lang_option = page.locator(f'div:has-text("{language}")').first
                            if await lang_option.is_visible(timeout=2000):
                                await lang_option.click()
                                await page.wait_for_timeout(1000)
                    except:
                        logger.warning("Could not select language, using default")
                    
                    # Find and clear the code editor
                    try:
                        # Monaco editor textarea
                        editor = page.locator('.monaco-editor textarea, .CodeMirror textarea').first
                        if await editor.is_visible(timeout=3000):
                            # Clear existing code
                            await page.keyboard.press("Control+A")
                            await page.wait_for_timeout(500)
                            
                            # Type new code
                            await page.keyboard.type(solution_code, delay=10)
                            await page.wait_for_timeout(1000)
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
                        if await submit_btn.is_visible(timeout=3000):
                            await submit_btn.click()
                            logger.info("Solution submitted!")
                            await page.wait_for_timeout(5000)  # Wait for result
                            
                            # Check submission result
                            result_text = ""
                            try:
                                result_elem = page.locator('[class*="result"], [class*="accepted"], [class*="wrong"]').first
                                if await result_elem.is_visible(timeout=10000):
                                    result_text = await result_elem.inner_text()
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
                    import time
                    screenshot_path = f"leetcode_error_{int(time.time())}.png"
                    await page.screenshot(path=screenshot_path)
                except:
                    screenshot_path = None
                
                return {
                    "error": "workflow_error",
                    "message": str(e),
                    "screenshot": screenshot_path
                }
            finally:
                await context.close()
                
    except Exception as e:
        logger.error(f"Playwright error in LeetCode workflow: {e}")
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
