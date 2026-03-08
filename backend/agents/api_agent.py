from tools.gmail_tool import read_gmail
from tools.slack_tool import send_slack_message
from tools.drive_tool import upload_to_drive


class APIAgent:

    def execute(self, task, user_context):

        tool = task["tool"]
        params = task.get("parameters", {})

        if tool == "read_gmail":
            return read_gmail(user_context, params)

        elif tool == "send_slack_message":
            return send_slack_message(user_context, params)

        elif tool == "upload_to_drive":
            return upload_to_drive(user_context, params)

        else:
            return {"error": "Unknown API tool"}