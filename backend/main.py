from fastapi import FastAPI
from api.routes import router as api_router

app = FastAPI(title="AgentOS Backend")

app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "AgentOS backend running"}