from pathlib import Path
import os

os.makedirs("workbench", exist_ok=True)


def read_file(path: str) -> str:
    p = Path("workbench") / path.lstrip("/")
    if not p.exists():
        return f"ERROR: {path} does not exist"
    return p.read_text(encoding="utf-8")


def write_file(path: str, content: str) -> str:
    p = Path("workbench") / path.lstrip("/")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} chars to {path}"


def update_todos(todos: list) -> str:
    return f"Todo list updated: {sum(1 for t in todos if t['status'] == 'completed')}/{len(todos)} completed"
