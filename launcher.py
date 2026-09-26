import subprocess
import time
import webbrowser
import os
import sys

# Configure stdout and stderr for UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def main():
    print("🚀 Booting up CodeD3mon-2048...")
    
    # 1. Start Frontend
    frontend_dir = os.path.join(os.getcwd(), 'frontend')
    next_bin = os.path.join(frontend_dir, 'node_modules', '.bin', 'next.cmd' if os.name == 'nt' else 'next')
    if not os.path.exists(next_bin):
        print("📦 Installing frontend dependencies (npm install)...")
        subprocess.run(['npm', 'install'], cwd=frontend_dir, shell=True, check=True)

    frontend_process = subprocess.Popen(
        ['npm', 'run', 'dev'], 
        cwd=frontend_dir,
        shell=True
    )
    
    # 2. Start Backend
    backend_dir = os.path.join(os.getcwd(), 'backend')
    python_exe = os.path.join(backend_dir, '.venv', 'Scripts', 'python.exe')
    if not os.path.exists(python_exe):
        python_exe = sys.executable
        
    backend_process = subprocess.Popen(
        [python_exe, 'main.py'],
        cwd=backend_dir,
        shell=True
    )
    
    # Wait for servers to spin up
    time.sleep(5)
    
    # 3. Open browser automatically
    webbrowser.open("http://localhost:3000")
    
    print("\n✅ System Online! Both servers are running in the background.")
    print("Use the 'Power Off' button on the Web Dashboard to cleanly shut down the servers.")
    
    try:
        # The backend process will exit automatically when the user clicks 'Power Off' on the website
        backend_process.wait()
    except KeyboardInterrupt:
        pass
    finally:
        print("\nShutting down systems gracefully...")
        # Kill the frontend node process tree
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(frontend_process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if backend_process.poll() is None:
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(backend_process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        sys.exit(0)

if __name__ == "__main__":
    main()
