#!/bin/bash
set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║      OpenEnv Peak — Linux/Mac Runner     ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check Python 3
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "Mac:           brew install python3"
    exit 1
fi

PY=$(python3 --version)
echo "  Using: $PY"

# Install deps
echo "  Installing dependencies..."
pip3 install fastapi "uvicorn[standard]" pydantic httpx python-multipart -q 2>/dev/null || \
pip3 install fastapi "uvicorn[standard]" pydantic httpx python-multipart -q --break-system-packages 2>/dev/null || \
pip3 install fastapi "uvicorn[standard]" pydantic httpx python-multipart -q --user

echo "  Starting server at http://127.0.0.1:7860"
echo ""
echo "  Dashboard:  http://127.0.0.1:7860/"
echo "  API Docs:   http://127.0.0.1:7860/docs"
echo "  Press CTRL+C to stop"
echo ""

python3 -m uvicorn app.main:app --host 127.0.0.1 --port 7860
