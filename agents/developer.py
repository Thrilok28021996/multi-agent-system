import json
from openai import OpenAI
import os
from tools import read_file, write_file, code_execution, run_command
from dotenv import load_dotenv

load_dotenv()
Model = os.getenv("MODEL")
MODEL_HOST = os.getenv("MODEL_HOST")
OPENAI_API_KEY = os.getenv("BACKEND")

# --- OpenAI Responses API tool schema (NOT input_schema) ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the full contents of a text file at the given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative or absolute file path",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write (overwrite) text content to a file at the given path. Creates parent dirs if needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "code_execution",
            "description": "Execute the file at the given path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative or absolute file path",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Execute a shell command inside the project root (e.g. mkdir, "
                "python -m venv, pip install -r requirements.txt, pytest). "
                "Returns stdout, stderr, and returncode. Destructive commands "
                "(rm, sudo, curl, wget, chmod, dd) are blocked."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute, e.g. 'python -m venv venv'",
                    }
                },
                "required": ["command"],
            },
        },
    },
]

TOOL_IMPL = {
    "read_file": read_file,
    "write_file": write_file,
    "code_execution": code_execution,
    "run_command": run_command,
}


def developer(tasks: str, context: str) -> tuple[str, str]:
    client = OpenAI(base_url=MODEL_HOST, api_key=OPENAI_API_KEY)
    # print(tasks.get("id"))
    # print(tasks.get("content"))
    target_file = (
        tasks.get("target_file")
        or "not specified - infer a reasonable path under the project root"
    )
    acceptance_criteria = tasks.get("acceptance_criteria") or []
    prompt = f"""Task ID: {tasks.get("id")}
        Status: {tasks.get("status")}
        Instructions: {tasks.get("content")}
        Target file: {target_file}
        Acceptance criteria: {", ".join(acceptance_criteria) if acceptance_criteria else "none specified - use the instructions as the criteria"}
        {f"Context from previous steps:\n{context}" if context else ""}"""
    messages = [
        {
            "role": "system",
            "content": (
                """You are a developer agent operating in a task loop controlled by an orchestrator.

INPUT: You will receive a task with: task_id, description,status, target_file (path, may or may not exist), and acceptance_criteria (list of conditions that define "done").

TOOLS:
- read_file(path)
- write_file(path, content)
- code_execution(path) — runs an existing file to check it executes/imports cleanly
- run_command(command) — runs a shell command in the project root (mkdir, python -m venv, pip install, pytest, etc.)

WORKFLOW:
1. If target_file exists → call read_file first. Modify ONLY the code relevant to the task description. Do not refactor unrelated code, change formatting/imports not tied to the task, or touch other files.
2. If target_file does not exist → create it via write_file with minimal necessary content to satisfy acceptance_criteria.
3. For file-level changes: after every write_file call, run code_execution on that file to validate it runs/imports cleanly. For project-level setup (directories, venv, installing dependencies, running test suites): use run_command.
4. If code_execution errors: read the traceback, patch the specific issue via write_file, re-run. Max 3 fix attempts per task.
5. If unresolved after 3 attempts → stop. Do not keep looping.

RETURN FORMAT (always JSON):
{
  "task_id": "<id>",
  "status": "completed" | "failed",
  "files_changed": ["path1", ...],
  "summary": "<1-2 sentence description of what changed>",
  "execution_output": "<last code_execution stdout/stderr>",
  "error": "<null, or reason if status is failed>"
}

CONSTRAINTS:
- Do not read/write/execute outside the project root.
- Do not install new dependencies unless explicitly permitted in the task; if a missing-package error blocks execution, report it in "error" rather than installing silently.
- Never guess at ambiguous requirements — if acceptance_criteria conflicts with existing code, return status "failed" with a clear error explaining the conflict instead of proceeding. """
            ),
        },
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model=Model,
        messages=messages,
        tools=tools,
        temperature=0.1,
    )
    msg = response.choices[0].message
    # print(msg)
    messages.append(msg.model_dump(exclude_none=True))

    print(msg)

    for tc in msg.tool_calls:
        fn_name = tc.function.name
        args = json.loads(tc.function.arguments)
        result = TOOL_IMPL[fn_name](**args)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result),
            }
        )
    return "completed", msg.content
