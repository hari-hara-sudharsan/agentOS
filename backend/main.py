# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from utils.error_handler import global_exception_handler
from utils.metrics import (
    get_metrics, get_metrics_content_type, 
    PrometheusMiddleware, set_system_info
)

from database.db import engine
from database.models import Base
from utils.rate_limiter import limiter

# Import all tools to register them
import tools.gmail_tool
import tools.slack_tool
import tools.drive_tool
import tools.calendar_tool
import tools.summarize_text
import tools.pic_tools
import tools.github_tool
import tools.discord_tool
import tools.salesforce_tool
import tools.linear_tool
import tools.azure_tool
import tools.leetcode_tool
import tools.billing_tool

# Import OpenClaw bridge (registers openclaw_* tools)
try:
    import agents.openclaw_bridge
except Exception as e:
    print(f"OpenClaw bridge not available: {e}")

app = FastAPI(title="AgentOS Backend", version="1.0.0")

print("\n" + "="*60)
print(">>> AGENTOS BACKEND RELOADED - FRESH PERMISSION LOGIC ACTIVE <<<")
print("="*60 + "\n")

# Set system info for metrics
import os
set_system_info(
    version="1.0.0", 
    environment=os.getenv("ENVIRONMENT", "development")
)

app.state.limiter = limiter

origins = [
    "http://localhost:3000"
]

# Add Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api")

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint for scraping"""
    return Response(
        content=get_metrics(),
        media_type=get_metrics_content_type()
    )

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(Exception, global_exception_handler)


@app.get("/")
def root():
    return {"message": "AgentOS backend running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)