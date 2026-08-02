from pathlib import Path
import os

import subprocess, shlex, os

os.makedirs("workbench", exist_ok=True)

PROJECT_ROOT = os.path.abspath("workbench")

BLOCKED = {"rm", "sudo", "curl", "wget", "chmod", "dd", ":(){"}


def run_command(command: str, timeout: int = 60) -> dict:
    tokens = shlex.split(command)
    if not tokens or tokens[0] in BLOCKED:
        return {
            "stdout": "",
            "stderr": f"Command '{tokens[0] if tokens else command}' is not permitted.",
            "returncode": 1,
        }
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Command timed out.", "returncode": -1}


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
            ["python3", str(p.resolve())],
            capture_output=True,
            text=True,
            timeout=90,
            cwd=PROJECT_ROOT,
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
