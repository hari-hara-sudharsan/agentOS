from registry.tool_registry import tool_registry
import os
import requests

def summarize_text(user_context, params, memory=None):
    text = params.get("text", "")
    
    # Check if input is specified - try to resolve from memory first
    if not text and memory and params.get("input"):
        input_key = params.get("input")
        res = memory.get(input_key)
        if res and isinstance(res, dict):
            # If the previous tool returned an error, propagate it
            if "error" in res:
                return {
                    "error": "input_tool_failed",
                    "message": f"Cannot summarize: {res.get('service', 'previous tool')} returned an error",
                    "upstream_error": res,
                    "details": res.get("details") or res.get("message", str(res))
                }
            text = res.get("text", str(res))
        elif res:
            text = str(res)
            
    # Fallback - try to get gmail result from memory if no explicit input
    if not text and memory:
        gmail_res = memory.get("read_gmail")
        if gmail_res and isinstance(gmail_res, dict):
            if "error" in gmail_res:
                # Return the error directly instead of trying to summarize it
                return {
                    "error": "input_tool_failed",
                    "message": "Cannot summarize: Gmail returned an error",
                    "upstream_error": gmail_res,
                    "details": gmail_res.get("details") or gmail_res.get("message", str(gmail_res))
                }
            text = gmail_res.get("text", str(gmail_res))
        elif gmail_res:
            text = str(gmail_res)
            
    if not text:
        return {"error": "no_text_provided", "message": "No text content available to summarize"}
        
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"summary": f"Simulated Summary: {str(text)[:100]}..."}
        
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "Summarize the following text."},
                    {"role": "user", "content": str(text)[:4000]}
                ]
            },
            timeout=15
        )
        data = response.json()
        if "choices" in data:
            return {"summary": data["choices"][0]["message"]["content"]}
        return {"error": "openai_api_error", "message": "OpenAI API error", "details": data}
    except Exception as e:
        return {"error": str(e)}

tool_registry.register("summarize_text", summarize_text)
