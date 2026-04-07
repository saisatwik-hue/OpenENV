"""
server/app.py
Required entry point for OpenEnv multi-mode deployment validation.
"""
import os
import uvicorn
from app.main import app

__all__ = ["app"]


def main():
    """Entry point called by `server` script in pyproject.toml."""
    uvicorn.run(
        "app.main:app",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "7860")),
        workers=1,
        log_level="info",
    )


if __name__ == "__main__":
    main()
