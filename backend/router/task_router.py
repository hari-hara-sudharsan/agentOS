from agents.api_agent import APIAgent
from agents.browser_agent import BrowserAgent
from utils.logger import logger


class TaskRouter:

    def __init__(self):

        self.api_agent = APIAgent()
        self.browser_agent = BrowserAgent()

    def execute_tool(self, task, user_context, memory):

        tool = task["tool"]
        logger.info(f"Executing tool: {tool}")

        if tool.startswith("browser_"):

            return self.browser_agent.execute(task, memory)

        else:

            return self.api_agent.execute(task, user_context, memory)