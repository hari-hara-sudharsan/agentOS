from registry.tool_registry import tool_registry


class APIAgent:

    def execute(self, task, user_context, memory=None):

        tool_name = task["tool"]
        params = task.get("parameters", {})
        
        # Merge input from task so tools can access it natively
        if "input" in task and task["input"]:
            params["input"] = task["input"]

        tool = tool_registry.get(tool_name)

        if not tool:
            return {"error": "tool not found"}

        import inspect
        sig = inspect.signature(tool)
        kwargs = {}
        if "user_context" in sig.parameters:
            kwargs["user_context"] = user_context
        if "params" in sig.parameters:
            kwargs["params"] = params
        if "memory" in sig.parameters:
            kwargs["memory"] = memory
        
        # fallback for old tools that just take (user_context, params)
        if not kwargs:
            return tool(user_context, params)
            
        return tool(**kwargs)