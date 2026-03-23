from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from utils.rate_limiter import limiter

from security.auth0_client import get_current_user
from executor.task_executor import TaskExecutor
from agents.planner_agent import create_plan
from registry.tool_registry import tool_registry

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

            # Log authorized tool execution
            from database.activity_logger import log_activity
            user_id = user.get("sub", "system")
            log_activity(
                user_id,
                action=f"tool_execution:{tool}",
                status="authorized"
            )

            executor.memory.store(tool, result)

            yield json.dumps({
                "event": "step_completed",
                "tool": tool,
                "result": result
            }) + "\n"

        except Exception as e:
            
            error_str = str(e)
            from database.activity_logger import log_activity
            user_id = user.get("sub", "system")

            if "step_up_required" in error_str:
                log_activity(
                    user_id,
                    action=f"awaiting_consent:{tool}",
                    status="pending"
                )
                yield json.dumps({
                    "event": "awaiting_consent",
                    "tool": tool,
                    "task": task
                }) + "\n"
                break

            if "Role" in error_str and "cannot execute tool" in error_str or "Tool not allowed" in error_str:
                # Log blocked tool execution
                log_activity(
                    user_id,
                    action=f"blocked_tool:{tool}",
                    status="denied"
                )
            
            yield json.dumps({
                "event": "step_failed",
                "tool": tool,
                "error": error_str
            }) + "\n"

        await asyncio.sleep(0.2)

    yield json.dumps({
        "event": "execution_finished"
    }) + "\n"


@router.post("/run-task-stream")
@limiter.limit("5/minute")
async def run_agent_task_stream(
    request: Request,
    task_request: TaskRequest,
    user=Depends(get_current_user)
):

    user_message = task_request.message

    plan = create_plan(user_message)

    return StreamingResponse(
        stream_execution(plan, task_executor, user),
        media_type="application/json"
    )

class ResumeRequest(BaseModel):
    task: dict

@router.post("/resume-task")
@limiter.limit("10/minute")
def resume_agent_task(
    request: Request,
    resume_req: ResumeRequest,
    user=Depends(get_current_user)
):
    """
    Job 4: Async Step-up Auth (Resume).
    Frontend calls this after user approves the step-up prompt.
    """
    task = resume_req.task
    if "params" not in task:
        task["params"] = {}
    
    # Indicate to the backend that consent has been confirmed
    task["params"]["consent_granted"] = True
    
    try:
        result = task_executor.router.execute_tool(
            task,
            user,
            task_executor.memory
        )
        # Log successful completion after step-up
        from database.activity_logger import log_activity
        log_activity(user.get("sub", "system"), action=f"step_up_approved:{task['tool']}", status="success")
        
        task_executor.memory.store(task["tool"], result)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/tools")
def list_tools():

    return {
        "available_tools": tool_registry.list_tools()
    }