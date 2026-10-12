"""
Universal Launcher for LearnCode AI.
Detects available packages and runs Streamlit or the Standalone Web Server.
"""
import sys
import subprocess
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    print("=======================================================")
    print(" [LearnCode AI] Master Platform Launcher")
    print("=======================================================")

    try:
        import streamlit
        print("[OK] Streamlit detected. Launching Streamlit dashboard...")
        app_path = os.path.join(os.path.dirname(__file__), "app.py")
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
    except ImportError:
        print("[*] Streamlit not detected in current environment.")
        print("Launching the built-in standalone web application (zero extra dependencies needed)...")
        from web_app import run_web_server
        run_web_server()

if __name__ == "__main__":
    main()
