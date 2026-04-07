from browser.browser_utils import take_screenshot
from browser.download_manager import save_download


def execute_browser_task(page, tool, params):

    try:

        if tool == "browser_open_site":

            url = params.get("url")

            page.goto(url)

            return {
                "status": "success",
                "message": f"✅ Opened website successfully",
                "url": url,
                "link": url,
                "title": page.title()
            }

        elif tool == "browser_login":

            page.fill(params["username_selector"], params["username"])
            page.fill(params["password_selector"], params["password"])

            page.click(params["submit_selector"])

            page.wait_for_timeout(3000)

            return {
                "status": "success",
                "message": "✅ Login completed successfully",
                "url": page.url,
                "link": page.url
            }

        elif tool == "browser_download_file":

            with page.expect_download() as download_info:

                page.click(params["download_selector"])

            download = download_info.value

            file_path = save_download(download)

            return {
                "status": "success",
                "message": f"✅ File downloaded successfully",
                "file_path": file_path,
                "file_name": download.suggested_filename
            }

    except Exception as e:

        screenshot = take_screenshot(page, "browser_error")

        return {
            "error": str(e),
            "screenshot": screenshot
        }