from browser.playwright_runner import run_browser_task


def electricity_bill_workflow():

    steps = [

        {
            "tool": "browser_open_site",
            "params": {
                "url": "https://example-electricity-portal.com"
            }
        },

        {
            "tool": "browser_login",
            "params": {
                "username_selector": "#username",
                "password_selector": "#password",
                "submit_selector": "#login",
                "username": "USER",
                "password": "PASS"
            }
        },

        {
            "tool": "browser_download_file",
            "params": {
                "download_selector": "#download-bill"
            }
        }

    ]

    results = []

    for step in steps:

        result = run_browser_task(
            step["tool"],
            step["params"]
        )

        results.append(result)

    return results
