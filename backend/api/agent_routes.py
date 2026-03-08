from fastapi import APIRouter, Depends
from pydantic import BaseModel

from security.auth0_client import get_current_user

router = APIRouter()


class TaskRequest(BaseModel):
    message: str


@router.post("/run-task")
def run_agent_task(
    request: TaskRequest,
    user=Depends(get_current_user)
):

    user_message = request.message

    # placeholder response until planner is implemented
    return {
        "user": user,
        "message_received": user_message,
        "status": "planner_not_connected_yet"
    }