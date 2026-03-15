from agents.api_agent import APIAgent
from agents.browser_agent import BrowserAgent
from utils.logger import logger
from security.auth0_client import get_user_role
from security.permission_validator import validate_permission
from security.tool_policy import authorize_tool


class TaskRouter:

    def __init__(self):

        self.api_agent = APIAgent()
        self.browser_agent = BrowserAgent()

    def execute_tool(self, task, user_context, memory):

        tool = task["tool"]
        logger.info(f"Executing tool: {tool}")
        
        authorize_tool(tool)

        role = get_user_role(user_context)

        validate_permission(role, tool)

        if tool.startswith("browser_"):

            return self.browser_agent.execute(task, memory)

        else:

            return self.api_agent.execute(task, user_context, memory)