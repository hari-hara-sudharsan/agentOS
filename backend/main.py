from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from utils.error_handler import global_exception_handler




from database.db import engine
from database.models import Base
from utils.rate_limiter import limiter

import tools.gmail_tool
import tools.slack_tool
import tools.drive_tool
import tools.calendar_tool
import tools.summarize_text

app = FastAPI(title="AgentOS Backend")

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

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(Exception, global_exception_handler)


@app.get("/")
def root():
    return {"message": "AgentOS backend running"}