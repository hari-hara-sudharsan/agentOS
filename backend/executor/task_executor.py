from router.task_router import TaskRouter
from memory.execution_memory import ExecutionMemory
import concurrent.futures


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

                for attempt in range(MAX_RETRIES):
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
                        if attempt == MAX_RETRIES - 1:
                            raise e

                self.memory.store(tool, result)

                results.append({
                    "tool": tool,
                    "status": "success",
                    "result": result
                })

            except Exception as e:

                results.append({
                    "tool": tool,
                    "status": "failed",
                    "error": str(e)
                })

        return {
            "goal": plan.get("goal"),
            "results": results,
            "memory": self.memory.get_all()
        }