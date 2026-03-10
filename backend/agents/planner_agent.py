from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
from config import config

llm = ChatOpenAI(
    openai_api_key=config.OPENAI_API_KEY,
    temperature=0
)

SYSTEM_PROMPT = """
You are the Planner Agent for AgentOS.

Your job is to convert a user's request into a structured list of tasks.

Each task must reference a tool.

Available tools:

read_gmail
send_slack_message
create_calendar_event
upload_to_drive
browser_open_site
browser_login
browser_download_file
summarize_text

Return JSON in this format:

{
 "goal": "...",
 "tasks": [
   {
     "step": 1,
     "tool": "tool_name",
     "description": "what this step does"
   }
 ]
}
"""


def create_plan(user_message):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages)

    try:
        plan = json.loads(response.content)
    except Exception:
        plan = {
            "goal": user_message,
            "tasks": []
        }

    return plan