# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from utils.error_handler import global_exception_handler

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

app = FastAPI(title="AgentOS Backend")

print("\n" + "="*60)
print(">>> AGENTOS BACKEND RELOADED - FRESH PERMISSION LOGIC ACTIVE <<<")
print("="*60 + "\n")

app.state.limiter = limiter

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api")

@app.get("/metrics")
def metrics():
    # Stub endpoint for Prometheus scraping. Implement actual app metrics in Phase 2.
    return "# HELP agentos_up AgentOS up status\n# TYPE agentos_up gauge\nagentos_up 1\n"

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