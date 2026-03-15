from router.task_router import TaskRouter
from memory.execution_memory import ExecutionMemory
import concurrent.futures
from database.activity_logger import log_activity


class TaskExecutor:

    def __init__(self):

        self.router = TaskRouter()
        self.memory = ExecutionMemory()

    def execute_plan(self, plan, user_context):

        tasks = plan.get("tasks", [])

        results = []

        for task in tasks:

            tool = task["tool"]

            try:
                MAX_RETRIES = 2
                retries = 0

                while retries <= MAX_RETRIES:
                    try:
                        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                            future = pool.submit(
                                self.router.execute_tool,
                                task,
                                user_context,
                                self.memory
                            )
                            
                            try:
                                result = future.result(timeout=10)
                                break
                            except concurrent.futures.TimeoutError:
                                raise TimeoutError("Tool execution timeout")
                            
                    except Exception as e:
                        retries += 1
                        if retries > MAX_RETRIES:
                            raise e

                output_key = task.get("output", tool)
                self.memory.store(output_key, result)

                user_id = user_context.get("sub", "system")

                log_activity(user_id, action=f"tool_execution:{tool}", status="authorized")
                log_activity(user_id, action=f"execute_tool_{tool}", status="success")

                results.append({
                    "tool": tool,
                    "status": "success",
                    "result": result
                })

            except Exception as e:
                
                error_str = str(e)
                user_id = user_context.get("sub", "system")

                if "Role" in error_str and "cannot execute tool" in error_str or "Tool not allowed" in error_str:
                    log_activity(user_id, action=f"blocked_tool:{tool}", status="denied")

                log_activity(user_id, action=f"execute_tool_{tool}", status="failed")

                results.append({
                    "tool": tool,
                    "status": "failed",
                    "error": error_str
                })

        return {
            "goal": plan.get("goal"),
            "results": results,
            "memory": self.memory.get_all()
        }