from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from utils.error_handler import global_exception_handler




from database.db import engine
from database.models import Base

app = FastAPI(title="AgentOS Backend")

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

app.add_exception_handler(Exception, global_exception_handler)


@app.get("/")
def root():
    return {"message": "AgentOS backend running"}