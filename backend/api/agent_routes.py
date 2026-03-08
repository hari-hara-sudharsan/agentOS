from fastapi import APIRouter, Depends
from pydantic import BaseModel

from security.auth0_client import get_current_user
from router.task_router import TaskRouter

router = APIRouter()

task_router = TaskRouter()


class TaskRequest(BaseModel):
    message: str


@router.post("/run-task")
def run_agent_task(
    request: TaskRequest,
    user=Depends(get_current_user)
):

    user_message = request.message

    result = task_router.execute(user_message, user)

    return result