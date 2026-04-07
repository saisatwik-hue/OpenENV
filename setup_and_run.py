#!/usr/bin/env python3
"""
OpenEnv Peak — Automatic Setup & Run Script
Run this ONE file to install everything and start the server.

Usage:
    python setup_and_run.py

Requirements: Python 3.9+  (no other pre-installed packages needed)
"""

import sys, os, subprocess, platform, shutil

MIN_PYTHON = (3, 9)
PORT = 7860

def run(cmd, **kw):
    return subprocess.run(cmd, shell=True, check=True, **kw)

def check(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True).returncode == 0

def banner(msg):
    print(f"\n{'─'*55}")
    print(f"  {msg}")
    print(f"{'─'*55}")

banner("OpenEnv Peak — Setup & Run")
print(f"  Python {sys.version.split()[0]} | {platform.system()} {platform.machine()}")

# ── 1. Python version check ───────────────────────────────────────────────────
if sys.version_info < MIN_PYTHON:
    print(f"\n✗ Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required. You have {sys.version_info.major}.{sys.version_info.minor}")
    print("  Download: https://python.org/downloads")
    sys.exit(1)
print(f"  ✓ Python version OK")

# ── 2. Find pip ───────────────────────────────────────────────────────────────
pip = "pip3" if check("pip3 --version") else "pip" if check("pip --version") else None
if not pip:
    print("\n✗ pip not found. Install pip: https://pip.pypa.io/en/stable/installation/")
    sys.exit(1)
print(f"  ✓ pip found: {pip}")

# ── 3. Install dependencies ───────────────────────────────────────────────────
banner("Installing dependencies…")
packages = ["fastapi==0.115.0", "uvicorn[standard]==0.30.6", "pydantic==2.9.2",
            "httpx==0.27.2", "python-multipart==0.0.9"]

already_installed = []
to_install = []
for pkg in packages:
    name = pkg.split("==")[0].split("[")[0]
    if check(f"{sys.executable} -c \"import {name.replace('-','_')}\""):
        already_installed.append(name)
    else:
        to_install.append(pkg)

if already_installed:
    print(f"  Already installed: {', '.join(already_installed)}")

if to_install:
    print(f"  Installing: {', '.join(to_install)}")
    # Try normal install first, then --break-system-packages for Linux
    install_cmd = f"{pip} install {' '.join(to_install)} -q"
    result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        # Try with --break-system-packages (needed on some Linux distros)
        result2 = subprocess.run(install_cmd + " --break-system-packages", shell=True, capture_output=True, text=True)
        if result2.returncode != 0:
            # Try creating a venv
            print("  Direct install failed, trying virtual environment…")
            venv_dir = os.path.join(os.path.dirname(__file__), ".venv")
            if not os.path.exists(venv_dir):
                run(f"{sys.executable} -m venv {venv_dir}")
            pip_venv = os.path.join(venv_dir, "bin", "pip") if platform.system() != "Windows" else os.path.join(venv_dir, "Scripts", "pip.exe")
            python_venv = os.path.join(venv_dir, "bin", "python") if platform.system() != "Windows" else os.path.join(venv_dir, "Scripts", "python.exe")
            run(f"{pip_venv} install {' '.join(to_install)} -q")
            # Restart with venv python
            print(f"\n  Re-running with venv Python…")
            os.execv(python_venv, [python_venv, __file__])
        else:
            print(f"  ✓ Installed (--break-system-packages)")
    else:
        print(f"  ✓ Installed")
else:
    print(f"  ✓ All dependencies already installed")

# ── 4. Verify imports ─────────────────────────────────────────────────────────
banner("Verifying installation…")
try:
    import fastapi, uvicorn, pydantic, httpx
    print(f"  ✓ fastapi {fastapi.__version__}")
    print(f"  ✓ uvicorn {uvicorn.__version__}")
    print(f"  ✓ pydantic {pydantic.__version__}")
    print(f"  ✓ httpx    {httpx.__version__}")
except ImportError as e:
    print(f"  ✗ Import error: {e}")
    print("\n  MANUAL FIX:")
    print(f"  {pip} install fastapi uvicorn[standard] pydantic httpx python-multipart")
    sys.exit(1)

# ── 5. Validate app can load ──────────────────────────────────────────────────
banner("Loading application…")
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
try:
    from app.data import EMAILS, CATEGORY_COUNTS
    print(f"  ✓ Dataset: {len(EMAILS)} emails loaded")
    print(f"  ✓ Categories: {CATEGORY_COUNTS}")
    from app.tasks.registry import TASK_REGISTRY
    for tid, tcls in TASK_REGISTRY.items():
        t = tcls()
        print(f"  ✓ {tid}: {t.name} ({len(t.get_emails())} emails, max {t.max_steps} steps)")
    from app.main import app
    print(f"  ✓ FastAPI app loaded")
except Exception as e:
    import traceback
    print(f"  ✗ Load error: {e}")
    traceback.print_exc()
    sys.exit(1)

# ── 6. Start server ───────────────────────────────────────────────────────────
banner(f"Starting server on http://127.0.0.1:{PORT}")
print(f"""
  Dashboard:  http://127.0.0.1:{PORT}/
  API Docs:   http://127.0.0.1:{PORT}/docs
  Health:     http://127.0.0.1:{PORT}/health
  Tasks:      http://127.0.0.1:{PORT}/tasks

  Press CTRL+C to stop
""")

os.chdir(script_dir)
try:
    uvicorn.run("app.main:app", host="127.0.0.1", port=PORT, reload=False,
                log_level="info", access_log=True)
except KeyboardInterrupt:
    print("\n\n  Server stopped.")
except Exception as e:
    print(f"\n  ✗ Server error: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)
