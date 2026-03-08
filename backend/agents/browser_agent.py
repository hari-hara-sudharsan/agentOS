from browser.playwright_runner import run_browser_task


class BrowserAgent:

    def execute(self, task, memory=None):

        tool = task["tool"]
        params = task.get("parameters", {})

        result = run_browser_task(tool, params)

        return result