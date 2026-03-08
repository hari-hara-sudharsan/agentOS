from fastapi import FastAPI
from api.routes import router as api_router

from database.db import engine
from database.models import Base

app = FastAPI(title="AgentOS Backend")

Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "AgentOS backend running"}