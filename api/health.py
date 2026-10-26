import sys
import traceback
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/api/health")
def health():
    result = {
        "status": "healthy",
        "sys_path": sys.path,
        "python_version": sys.version,
    }
    try:
        import main
        result["main_import"] = "SUCCESS"
    except Exception as e:
        result["main_import"] = f"FAILED: {e}"
        result["traceback"] = traceback.format_exc()

    return JSONResponse(result)
