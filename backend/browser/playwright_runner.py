from playwright.async_api import async_playwright
from browser.browser_tasks import execute_browser_task
import asyncio


def run_browser_task(tool, params):
    """
    Synchronous wrapper for async Playwright to avoid asyncio loop conflicts.
    Detects if event loop is running and uses appropriate execution method.
    """
    import concurrent.futures
    
    try:
        # Check if there's a running event loop
        try:
            loop = asyncio.get_running_loop()
            # There's a running loop - execute in a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run_browser_in_new_loop, tool, params)
                result = future.result(timeout=60)  # 1 minute timeout
                return result
        except RuntimeError:
            # No running loop - safe to create our own
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(_run_browser_task_async(tool, params))
                return result
            finally:
                loop.close()
    except Exception as e:
        return {
            "error": "browser_task_error",
            "message": f"Error executing browser task: {str(e)}"
        }


def _run_browser_in_new_loop(tool, params):
    """Helper function to run async code in a new event loop in a separate thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run_browser_task_async(tool, params))
    finally:
        loop.close()


async def _run_browser_task_async(tool, params):
    """Async implementation of browser task execution"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        
        result = await execute_browser_task_async(page, tool, params)
        
        await browser.close()
        return result


async def execute_browser_task_async(page, tool, params):
    """Async version of execute_browser_task"""
    from browser.browser_utils import take_screenshot_async
    from browser.download_manager import save_download
    
    try:
        if tool == "browser_open_site":
            url = params.get("url")
            await page.goto(url)
            return {"status": "site_opened"}
        
        elif tool == "browser_login":
            await page.fill(params["username_selector"], params["username"])
            await page.fill(params["password_selector"], params["password"])
            await page.click(params["submit_selector"])
            await page.wait_for_timeout(3000)
            return {"status": "login_success"}
        
        elif tool == "browser_download_file":
            async with page.expect_download() as download_info:
                await page.click(params["download_selector"])
            download = await download_info.value
            file_path = save_download(download)
            return {
                "status": "download_complete",
                "file_path": file_path
            }
        
        elif tool == "browser_search":
            # Handle browser search for LeetCode daily
            query = params.get("query", "")
            await page.goto(f"https://www.google.com/search?q={query}", timeout=30000)
            await page.wait_for_load_state("domcontentloaded")
            
            # Extract search results text
            try:
                content = await page.inner_text("body")
                return {"status": "success", "text": content[:2000]}  # Limit text
            except:
                return {"status": "success", "text": "Could not extract search results"}
    
    except Exception as e:
        screenshot = await take_screenshot_async(page, "browser_error")
        return {
            "error": str(e),
            "screenshot": screenshot
        }