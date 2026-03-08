from registry.tool_registry import tool_registry


class APIAgent:

    def execute(self, task, user_context, memory=None):

        tool_name = task["tool"]
        params = task.get("parameters", {})

        tool = tool_registry.get(tool_name)

        if not tool:
            return {"error": "tool not found"}

        return tool(user_context, params)