from browser.playwright_runner import run_browser_task
from browser.workflows import electricity_bill_workflow


class BrowserAgent:

    def execute(self, task, memory=None):

        tool = task["tool"]

        if tool == "electricity_bill_workflow":

            return electricity_bill_workflow()

        return run_browser_task(
            tool,
            task.get("parameters", {})
        )