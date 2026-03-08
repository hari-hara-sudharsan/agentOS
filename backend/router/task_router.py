from agents.api_agent import APIAgent
from agents.browser_agent import BrowserAgent
from agents.planner_agent import create_plan


class TaskRouter:

    def __init__(self):

        self.api_agent = APIAgent()
        self.browser_agent = BrowserAgent()

    def execute(self, user_message, user_context):

        # Step 1: create plan
        plan = create_plan(user_message)

        tasks = plan.get("tasks", [])

        results = []

        # Step 2: execute tasks
        for task in tasks:

            tool = task["tool"]

            try:

                if tool.startswith("browser_"):

                    result = self.browser_agent.execute(task)

                else:

                    result = self.api_agent.execute(task, user_context)

                results.append({
                    "tool": tool,
                    "status": "success",
                    "result": result
                })

            except Exception as e:

                results.append({
                    "tool": tool,
                    "status": "failed",
                    "error": str(e)
                })

        return {
            "goal": plan.get("goal"),
            "steps_executed": results
        }