from registry.tool_registry import tool_registry
import os
import requests

def summarize_text(user_context, params, memory=None):
    text = params.get("text", "")
    if not text and memory:
        gmail_res = memory.get("read_gmail")
        if gmail_res and isinstance(gmail_res, dict):
            text = gmail_res.get("text", str(gmail_res))
        elif gmail_res:
            text = str(gmail_res)
    if not text:
        return {"error": "no text provided"}
        
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
        return {"error": "openai api error", "details": data}
    except Exception as e:
        return {"error": str(e)}

tool_registry.register("summarize_text", summarize_text)
