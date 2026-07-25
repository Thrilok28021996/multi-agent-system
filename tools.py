from pathlib import Path
import os
import subprocess

os.makedirs("workbench", exist_ok=True)


def read_file(path: str) -> str:
    if not path or path.strip() in ("", "/", "."):
        return "ERROR: no filename provided. You must pass a specific file path, e.g. 'app.py'."
    p = Path("workbench") / path.lstrip("/")
    if p.is_dir():
        return f"ERROR: {path} is a directory, not a file"
    if not p.exists():
        return f"ERROR: {path} does not exist"
    return p.read_text(encoding="utf-8")


def write_file(path: str, content: str) -> str:
    p = Path("workbench") / path.lstrip("/")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"File written to path='{path}' ({len(content)} chars)"

def code_execution(path: str) -> str:
    if not path or path.strip() in ("", "/", "."):
        return "ERROR: no filename provided. You must pass a specific file path, e.g. 'app.py'."
    p = Path("workbench") / path.lstrip("/")
    if p.is_dir():
        return f"ERROR: {path} is a directory, not a file"
    if not p.exists():
        return f"ERROR: {path} does not exist"

    try:
        result = subprocess.run(
            ["python3", str(p)],
            capture_output=True,
            text=True,
            timeout=90,
            cwd="workbench",
        )
    except subprocess.TimeoutExpired:
        return f"ERROR: execution of {path} timed out after 90s"

    output = f"return_code={result.returncode}\n"
    if result.stdout:
        output += f"stdout:\n{result.stdout}\n"
    if result.stderr:
        output += f"stderr:\n{result.stderr}\n"
    return output


def update_todos(todos: list) -> str:
    return f"Todo list updated: {sum(1 for t in todos if t['status'] == 'completed')}/{len(todos)} completed"
