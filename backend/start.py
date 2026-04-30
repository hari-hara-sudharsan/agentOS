import os
import subprocess

port = os.getenv("PORT", "8000")
print(f"Starting on port {port}")

subprocess.run([
    "uvicorn",
    "main:app",
    "--host", "0.0.0.0",
    "--port", port
])
