import os
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("=" * 60)
    print("Starting Verity: Pre-Publication Brand Governance Platform")
    print("Accessible locally at: http://127.0.0.1:8000")
    print("Interactive API docs at: http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
