from agents.api_agent import APIAgent
from router.task_router import TaskRouter
from security.auth0_client import ConsentRequiredException
import traceback
import tools.gmail_tool

router = TaskRouter()

task = {
    "tool": "send_gmail",
    "parameters": {
        "to": "test@test.com",
        "subject": "Test",
        "body": "Test"
    }
}
user = {"sub": "google-oauth2|12345"}

try:
    result = router.execute_tool(task, user, None)
    print("SUCCESS", result)
except ConsentRequiredException as e:
    print("CAUGHT ConsentRequiredException!", e.approval_id)
except Exception as e:
    print("CAUGHT GENERIC EXCEPTION:", type(e).__name__)
    print(repr(e))
    traceback.print_exc()
