from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from utils.rate_limiter import limiter

from security.auth0_client import get_current_user, ConsentRequiredException
from executor.task_executor import TaskExecutor
from agents.planner_agent import create_plan
from registry.tool_registry import tool_registry

from fastapi.responses import StreamingResponse
import json
import asyncio
import time

router = APIRouter()

task_executor = TaskExecutor()


class TaskRequest(BaseModel):
    message: str


async def stream_execution(plan, executor, user):
    from database.analytics_repository import record_agent_execution
    from database.activity_logger import log_activity

    tasks = plan.get("tasks", [])
    user_id = user.get("sub", "system")

    yield json.dumps({
        "event": "plan_created",
        "goal": plan.get("goal")
    }) + "\n"

    for task in tasks:

        tool = task["tool"]
        start_time = time.time()

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

            execution_time = time.time() - start_time
            
            # Log authorized tool execution (non-critical, wrap in try/except)
            try:
                log_activity(
                    user_id,
                    action=f"tool_execution:{tool}",
                    status="authorized"
                )
            except Exception as log_err:
                print(f"[WARN] Failed to log activity: {log_err}")
            
            # Record analytics (non-critical)
            try:
                record_agent_execution(
                    user_id=user_id,
                    task_name=plan.get("goal", tool),
                    execution_time=int(execution_time * 1000) / 1000,  # milliseconds to seconds
                    status="success",
                    tool_name=tool
                )
            except Exception as analytics_err:
                print(f"[WARN] Failed to record analytics: {analytics_err}")

            executor.memory.store(tool, result)

            yield json.dumps({
                "event": "step_completed",
                "tool": tool,
                "result": result
            }) + "\n"

        except ConsentRequiredException as ce:
            execution_time = time.time() - start_time
            
            try:
                log_activity(
                    user_id,
                    action=f"awaiting_consent:{tool}",
                    status="pending"
                )
            except:
                pass
            
            yield json.dumps({
                "event": "pending_approval",
                "tool": tool,
                "task": task,
                "approval_id": ce.approval_id,
                "binding_message": ce.binding_message
            }) + "\n"
            break

        except Exception as e:
            execution_time = time.time() - start_time
            error_str = str(e)
            
            if "pending_approval_required" in error_str or e.__class__.__name__ == "ConsentRequiredException":
                try:
                    log_activity(
                        user_id,
                        action=f"awaiting_consent:{tool}",
                        status="pending"
                    )
                except:
                    pass
                yield json.dumps({
                    "event": "pending_approval",
                    "tool": tool,
                    "task": task,
                    "approval_id": getattr(e, "approval_id", None),
                    "binding_message": getattr(e, "binding_message", None)
                }) + "\n"
                break
                

            if "Role" in error_str and "cannot execute tool" in error_str or "Tool not allowed" in error_str:
                # Log blocked tool execution
                try:
                    log_activity(
                        user_id,
                        action=f"blocked_tool:{tool}",
                        status="denied"
                    )
                except:
                    pass
            
            # Record failed execution (non-critical)
            try:
                record_agent_execution(
                    user_id=user_id,
                    task_name=plan.get("goal", tool),
                    execution_time=int(execution_time * 1000) / 1000,
                    status="failed",
                    tool_name=tool,
                    error_message=error_str[:500]  # Truncate long errors
                )
            except Exception as analytics_err:
                print(f"[WARN] Failed to record analytics: {analytics_err}")
            
            yield json.dumps({
                "event": "step_failed",
                "tool": tool,
                "error": error_str + f" [CLASS: {e.__class__.__name__}]"
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
    from database.analytics_repository import record_agent_execution
    from database.activity_logger import log_activity
    
    task = resume_req.task
    user_id = user.get("sub", "system")
    
    if "params" not in task:
        task["params"] = {}

    # Indicate to the backend that consent has been confirmed
    task["params"]["consent_granted"] = True
    if "approval_id" in task:
        task["params"]["approval_id"] = task["approval_id"]
    elif task.get("params", {}).get("approval_id"):
        task["params"]["approval_id"] = task["params"]["approval_id"]
    
    start_time = time.time()
    
    try:
        result = task_executor.router.execute_tool(
            task,
            user,
            task_executor.memory
        )
        execution_time = time.time() - start_time
        
        # Log successful completion after step-up (non-critical)
        try:
            log_activity(user_id, action=f"step_up_approved:{task['tool']}", status="success")
        except:
            pass
        
        # Record analytics (non-critical)
        try:
            record_agent_execution(
                user_id=user_id,
                task_name=f"Approved: {task['tool']}",
                execution_time=int(execution_time * 1000) / 1000,
                status="success",
                tool_name=task['tool']
            )
        except:
            pass
        
        task_executor.memory.store(task["tool"], result)
        return {"status": "success", "result": result}
    except Exception as e:
        execution_time = time.time() - start_time
        
        try:
            record_agent_execution(
                user_id=user_id,
                task_name=f"Approved: {task['tool']}",
                execution_time=int(execution_time * 1000) / 1000,
                status="failed",
                tool_name=task['tool'],
                error_message=str(e)[:500]
            )
        except:
            pass
        
        return {"status": "error", "error": str(e)}


@router.get("/tools")
def list_tools():

    return {
        "available_tools": tool_registry.list_tools()
    }