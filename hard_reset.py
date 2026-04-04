import os
import signal
import subprocess
import time
import shutil

def hard_reset():
    print("🚀 HARD RESET INITIATED")
    
    # 1. Clear __pycache__ folders
    print("🧹 Clearing Python caches...")
    backend_dir = r"c:\Users\Windows\agentos\backend"
    for root, dirs, files in os.walk(backend_dir):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))
            print(f"   Deleted {os.path.join(root, '__pycache__')}")

    # 2. Find and kill Python processes running uvicorn
    print("🛑 Killing stale processes...")
    try:
        # We'll use taskkill on Windows to be thorough
        subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], capture_output=True)
        print("   Killed Python processes.")
    except Exception as e:
        print(f"   Error killing processes: {e}")

    print("✅ RESET COMPLETE.")
    print("👉 Please restart your backend server now by running:")
    print("   cd backend")
    print("   uvicorn main:app --reload")

if __name__ == "__main__":
    hard_reset()
