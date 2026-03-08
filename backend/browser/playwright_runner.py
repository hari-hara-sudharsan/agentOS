from playwright.sync_api import sync_playwright
from browser.browser_tasks import execute_browser_task


def run_browser_task(tool, params):

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        result = execute_browser_task(page, tool, params)

        browser.close()

        return result