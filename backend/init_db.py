"""
Initialize database tables.
Run this after any model changes: python init_db.py

Use --reset flag to drop and recreate all tables (DELETES ALL DATA)
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import engine, Base
from database.models import User, Integration, ActivityLog, AgentAnalytics, Approval

def init_database(reset=False):
    from sqlalchemy import inspect, text
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if reset and existing_tables:
        print("⚠️  RESET MODE: Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("✓ Tables dropped")
    
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created/updated successfully!")
    
    # List tables and their columns
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nDatabase tables:")
    for table in tables:
        columns = [col['name'] for col in inspector.get_columns(table)]
        print(f"  • {table}: {', '.join(columns)}")

def check_schema():
    """Check if schema is up to date with models."""
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    issues = []
    
    # Check ActivityLog
    if 'activity_logs' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('activity_logs')]
        if 'details' not in cols:
            issues.append("activity_logs missing 'details' column")
    
    # Check AgentAnalytics
    if 'agent_analytics' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('agent_analytics')]
        if 'tool_name' not in cols:
            issues.append("agent_analytics missing 'tool_name' column")
        if 'error_message' not in cols:
            issues.append("agent_analytics missing 'error_message' column")
    
    # Check Approval
    if 'approvals' not in inspector.get_table_names():
        issues.append("approvals table missing")
    
    return issues

if __name__ == "__main__":
    reset_mode = "--reset" in sys.argv
    
    # Check if schema is outdated
    issues = check_schema()
    
    if issues and not reset_mode:
        print("⚠️  Schema issues detected:")
        for issue in issues:
            print(f"   • {issue}")
        print("\n🔧 Run with --reset to fix: python init_db.py --reset")
        print("   WARNING: This will delete all existing data!")
        sys.exit(1)
    
    init_database(reset=reset_mode)
