import os
from pathlib import Path

def get_local_context_snippet(path: str = ".") -> dict:
    try:
        cwd = str(Path(path).resolve())
        items = sorted(os.listdir(cwd))
        sample = items[:50]
        return {"cwd": cwd, "count": len(items), "sample_files": sample}
    except Exception as e:
        return {"cwd": path, "error": str(e)}
