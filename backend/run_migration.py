"""Quick test: run auto_migrate_db to add missing columns"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import engine, Base
from database.models import *

# Create any new tables
Base.metadata.create_all(bind=engine)

# Now migrate missing columns
from sqlalchemy import inspect, text

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
        continue
    
    existing_cols = {col["name"] for col in inspector.get_columns(table_name)}
    model_cols = {col.name: col for col in table.columns}
    
    missing = set(model_cols.keys()) - existing_cols
    if not missing:
        continue
    
    print(f"Migrating '{table_name}': adding {len(missing)} column(s)")
    
    with engine.connect() as conn:
        for col_name in missing:
            col = model_cols[col_name]
            col_type_str = str(col.type).upper()
            sqlite_type = "TEXT"
            for sa_type, sq_type in type_map.items():
                if sa_type in col_type_str:
                    sqlite_type = sq_type
                    break
            
            sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{col_name}" {sqlite_type} NULL'
            try:
                conn.execute(text(sql))
                print(f"  Added: {col_name} ({sqlite_type})")
            except Exception as e:
                print(f"  Skip {col_name}: {e}")
        conn.commit()

# Verify
inspector = inspect(engine)
cols = [c['name'] for c in inspector.get_columns('approvals')]
print(f"\nApprovals now has {len(cols)} columns")
print(f"scope_weaver_analysis present: {'scope_weaver_analysis' in cols}")
print(f"shadow_simulation present: {'shadow_simulation' in cols}")
print("Done!")
