from router.task_router import TaskRouter
from memory.execution_memory import ExecutionMemory


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

                result = self.router.execute_tool(
                    task,
                    user_context,
                    self.memory
                )

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