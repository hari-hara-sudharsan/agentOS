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

def auto_migrate_db():
    """
    Safely add missing columns to existing tables without dropping data.
    Uses ALTER TABLE ADD COLUMN for SQLite compatibility.
    """
    from sqlalchemy import inspect, text, Column, Integer, String, Text, Float, Boolean, DateTime
    
    type_map = {
        "VARCHAR": "TEXT",
        "TEXT": "TEXT",
        "INTEGER": "INTEGER",
        "FLOAT": "REAL",
        "BOOLEAN": "INTEGER",
        "DATETIME": "TEXT",
    }
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    for table_name, table in Base.metadata.tables.items():
        if table_name not in existing_tables:
            continue  # create_all will handle new tables
        
        existing_cols = {col["name"] for col in inspector.get_columns(table_name)}
        model_cols = {col.name: col for col in table.columns}
        
        missing = set(model_cols.keys()) - existing_cols
        if not missing:
            continue
        
        print(f"🔄 Auto-migrating table '{table_name}': adding {len(missing)} missing column(s)")
        
        with engine.connect() as conn:
            for col_name in missing:
                col = model_cols[col_name]
                col_type_str = str(col.type)
                # Map SQLAlchemy types to SQLite types
                sqlite_type = "TEXT"
                for sa_type, sq_type in type_map.items():
                    if sa_type in col_type_str.upper():
                        sqlite_type = sq_type
                        break
                
                nullable = "NULL" if col.nullable else "NOT NULL"
                default = ""
                if col.default is not None:
                    default = f" DEFAULT NULL"
                elif not col.nullable:
                    if sqlite_type in ("INTEGER", "REAL"):
                        default = " DEFAULT 0"
                    else:
                        default = " DEFAULT ''"
                
                sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{col_name}" {sqlite_type} {nullable}{default}'
                try:
                    conn.execute(text(sql))
                    print(f"   ✅ Added column: {col_name} ({sqlite_type})")
                except Exception as e:
                    if "duplicate column" in str(e).lower():
                        pass  # Column already exists
                    else:
                        print(f"   ⚠️ Could not add column {col_name}: {e}")
            conn.commit()
    
    print("✅ Database schema is up to date")

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
    "http://localhost:3000",          # for local frontend dev
    "http://localhost:8000",
    # "https://agent-bkg2z5sde-first-intern.vercel.app",
    # "https://agent-bap3k3x86-first-intern.vercel.app",
    "*",  # Allow all origins (for testing, consider restricting in production)
    "https://agentos-backend-tjx6.onrender.com"
]

# Add Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
auto_migrate_db()  # Add any missing columns to existing tables

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