import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(command, cwd=None, shell=False):
    """Run a shell command and print output."""
    print(f"🔄 Running: {' '.join(command) if isinstance(command, list) else command}")
    try:
        subprocess.check_call(command, cwd=cwd, shell=shell)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing command: {e}")
        sys.exit(1)

def main():
    print("🚀 Starting CryptoScout Setup & Launch...")
    
    # 1. Check/Install uv
    if shutil.which("uv") is None:
        print("⚠️ 'uv' not found. Installing uv via pip...")
        run_command([sys.executable, "-m", "pip", "install", "uv"])
    else:
        print("✅ 'uv' is installed.")

    # 2. Create Virtual Environment
    venv_dir = Path(".venv")
    if not venv_dir.exists():
        print(f"🔨 Creating virtual environment in {venv_dir}...")
        run_command(["uv", "venv"])
    else:
        print(f"✅ Virtual environment found at {venv_dir}.")

    # 3. Install Requirements
    req_file = Path("requirements.txt")
    if req_file.exists():
        print("📦 Installing dependencies from requirements.txt...")
        run_command(["uv", "pip", "install", "-r", "requirements.txt"])
    else:
        print("⚠️ requirements.txt not found! Skipping installation.")

    # 4. Run Streamlit Server
    print("✨ Setup complete. Launching Streamlit App...")
    
    # Determine path to venv python/streamlit
    if os.name == "nt":
        python_exe = venv_dir / "Scripts" / "python.exe"
        streamlit_exe = venv_dir / "Scripts" / "streamlit.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
        streamlit_exe = venv_dir / "bin" / "streamlit"

    # Fallback if standard venv structure isn't exactly as expected, 
    # but uv usually follows standard venv.
    
    app_file = "app.py"
    if not Path(app_file).exists():
        print(f"❌ {app_file} not found. Cannot launch app.")
        sys.exit(1)

    # Launch using `python -m streamlit run app.py` from the venv
    launch_cmd = [str(python_exe), "-m", "streamlit", "run", app_file]
    
    try:
        subprocess.call(launch_cmd)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user.")

if __name__ == "__main__":
    main()
