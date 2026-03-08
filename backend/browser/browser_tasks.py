def execute_browser_task(page, tool, params):

    if tool == "browser_open_site":

        url = params.get("url")

        page.goto(url)

        return {"status": "site_opened", "url": url}


    elif tool == "browser_login":

        username_selector = params.get("username_selector")
        password_selector = params.get("password_selector")
        submit_selector = params.get("submit_selector")

        username = params.get("username")
        password = params.get("password")

        page.fill(username_selector, username)
        page.fill(password_selector, password)

        page.click(submit_selector)

        page.wait_for_timeout(3000)

        return {"status": "login_attempted"}


    elif tool == "browser_download_file":

        download_selector = params.get("download_selector")

        page.click(download_selector)

        page.wait_for_timeout(3000)

        return {"status": "download_triggered"}


    else:

        return {"error": "unknown_browser_tool"}