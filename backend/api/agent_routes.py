from fastapi import APIRouter, Depends
from pydantic import BaseModel

from security.auth0_client import get_current_user
from executor.task_executor import TaskExecutor
from agents.planner_agent import create_plan

from fastapi.responses import StreamingResponse
import json
import asyncio

router = APIRouter()

task_executor = TaskExecutor()


class TaskRequest(BaseModel):
    message: str


@router.post("/run-task")
async def run_agent_task(
    request: TaskRequest,
    user=Depends(get_current_user)
):

    user_message = request.message

    plan = create_plan(user_message)

    async def stream_results():
        
        yield json.dumps({"status": "plan_created", "plan": plan}) + "\n"
        await asyncio.sleep(0.1)

        result = task_executor.execute_plan(plan, user)

        yield json.dumps({"status": "execution_complete", "result": result}) + "\n"

    return StreamingResponse(stream_results(), media_type="application/x-ndjson")