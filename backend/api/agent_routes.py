from fastapi import APIRouter, Depends
from pydantic import BaseModel

from security.auth0_client import get_current_user
from executor.task_executor import TaskExecutor
from agents.planner_agent import create_plan

router = APIRouter()

task_executor = TaskExecutor()


class TaskRequest(BaseModel):
    message: str


@router.post("/run-task")
def run_agent_task(
    request: TaskRequest,
    user=Depends(get_current_user)
):

    user_message = request.message

    plan = create_plan(user_message)

    result = task_executor.execute_plan(plan, user)

    return result