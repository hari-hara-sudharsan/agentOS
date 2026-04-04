from registry.tool_registry import tool_registry
from utils.logger import logger


class APIAgent:

    def execute(self, task, user_context, memory=None):

        tool_name = task["tool"]
        params = task.get("parameters", {}).copy()
        
        # Resolve input from memory if specified
        if memory and "input" in task and task["input"]:
            input_key = task["input"]
            input_value = memory.get(input_key)
            
            if input_value:
                logger.info(f"Resolved input '{input_key}' from memory for {tool_name}")
                
                # Extract text content from result objects
                if isinstance(input_value, dict):
                    # If result has a 'text' key, use that
                    if "text" in input_value:
                        text_content = input_value["text"]
                    # If it's a Gmail result, reconstruct text
                    elif "messages" in input_value:
                        text_content = input_value.get("text", str(input_value))
                    else:
                        text_content = str(input_value)
                else:
                    text_content = str(input_value)
                
                # Merge resolved input into parameters
                # For summarize_text, inject as 'text'
                # For other tools, tools can read from memory directly
                if tool_name == "summarize_text" and "text" not in params:
                    params["text"] = text_content
                else:
                    params["input"] = input_key
            else:
                logger.warning(f"Input key '{input_key}' not found in memory for {tool_name}")
                # Fall back to passing the key as-is for tools to resolve
                params["input"] = input_key
        elif "input" in task and task["input"]:
            # No memory available, pass input key as parameter
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