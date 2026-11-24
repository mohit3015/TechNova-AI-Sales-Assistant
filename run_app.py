"""
=============================================================================
TechNova AI Sales Assistant - Unified Dual Runner (FastAPI + Streamlit)
=============================================================================
📌 ROLE & PURPOSE:
   Yeh utility script ek hi command se dono servers (FastAPI Backend + Streamlit Frontend)
   ko simultaneously start karti hai:
   - FastAPI Server: http://127.0.0.1:8000
   - Streamlit UI:   http://localhost:8501

🎯 USE CASE:
   Terminal mein ek single command run karein:
   `python run_app.py`
=============================================================================
"""

import sys
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def run_full_stack():
    print("=" * 65)
    print(" TechNova AI Sales Assistant - Starting Full Stack Application ")
    print("=" * 65)
    
    python_exe = sys.executable

    # 1. Start FastAPI Backend on Port 8000
    print("\n[1/2] Starting FastAPI Backend on http://127.0.0.1:8000...")
    fastapi_proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(PROJECT_ROOT)
    )

    # Wait for FastAPI to warm up
    time.sleep(2)

    # 2. Start Streamlit Frontend on Port 8501
    print("\n[2/2] Starting Streamlit Frontend on http://localhost:8501...")
    try:
        streamlit_proc = subprocess.Popen(
            [python_exe, "-m", "streamlit", "run", "frontend/streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"],
            cwd=str(PROJECT_ROOT)
        )
        print("\n Application is LIVE! Press Ctrl+C in terminal to stop both servers.")
        streamlit_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
    finally:
        fastapi_proc.terminate()
        try:
            streamlit_proc.terminate()
        except Exception:
            pass
        print(" Servers stopped gracefully.")


if __name__ == "__main__":
    run_full_stack()
