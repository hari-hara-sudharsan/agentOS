from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
from config import config

llm = ChatOpenAI(
    openai_api_key=config.OPENAI_API_KEY,
    temperature=0
)

SYSTEM_PROMPT = """
You are the planning agent of AgentOS.

Your job is to convert a user's request into a structured execution plan.

Rules:
1. Break tasks into atomic steps.
2. Use only available tools.
3. If information must be retrieved first, add a retrieval step.
4. Ensure output is valid JSON.
5. Each task must contain step, tool, description, and optionally input/output references to pass data.

Available tools:
- read_gmail
- send_slack_message
- upload_to_drive
- create_calendar_event
- browser_open_site
- browser_login
- browser_download_file
- summarize_text

Return format:

{
 "goal": "...",
 "tasks":[
   {
     "step":1,
     "tool":"tool_name",
     "parameters": {"query": "optional_search_term"},
     "input":"optional_input_from_memory_key",
     "output":"optional_memory_key_to_save",
     "description":"task explanation"
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