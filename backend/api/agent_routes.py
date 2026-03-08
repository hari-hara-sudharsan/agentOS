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


async def stream_execution(plan, executor, user):

    tasks = plan.get("tasks", [])

    yield json.dumps({
        "event": "plan_created",
        "goal": plan.get("goal")
    }) + "\n"

    for task in tasks:

        tool = task["tool"]

        yield json.dumps({
            "event": "step_started",
            "tool": tool
        }) + "\n"

        try:

            result = executor.router.execute_tool(
                task,
                user,
                executor.memory
            )

            executor.memory.store(tool, result)

            yield json.dumps({
                "event": "step_completed",
                "tool": tool,
                "result": result
            }) + "\n"

        except Exception as e:

            yield json.dumps({
                "event": "step_failed",
                "tool": tool,
                "error": str(e)
            }) + "\n"

        await asyncio.sleep(0.2)

    yield json.dumps({
        "event": "execution_finished"
    }) + "\n"


@router.post("/run-task")
async def run_agent_task(
    request: TaskRequest,
    user=Depends(get_current_user)
):

    user_message = request.message

    plan = create_plan(user_message)

    return StreamingResponse(
        stream_execution(plan, task_executor, user),
        media_type="application/x-ndjson"
    )