import hashlib
import json
from openai import OpenAI
import os
from tools import read_file, write_file, code_execution, run_command,PROJECT_ROOT
from dotenv import load_dotenv

load_dotenv()
Model = os.getenv("MODEL")
MODEL_HOST = os.getenv("MODEL_HOST")
OPENAI_API_KEY = os.getenv("BACKEND")

# No fixed turn ceiling. The loop runs until the model emits a final
# plain-text answer, OR until stuck-loop detection trips (below).
MAX_REPEAT_CALLS = 3  # same (tool, args) fired this many times consecutively -> abort
MAX_REPEAT_RESULTS = 3  # same (tool, result) returned this many times consecutively, despite varying args -> abort

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
                "Execute a shell command inside the project root (e.g. ls, mkdir, "
                "python -m venv, pip install -r requirements.txt, pytest). Use this "
                "for directory listing/inspection too (there is no separate list_dir tool). "
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
    client = OpenAI(base_url=MODEL_HOST, api_key=os.environ["OMNIROUTE_API_KEY"])
    target_file = (
        tasks.get("target_file")
        or f"not specified - infer a reasonable path under the project root, derived from the task instructions"
    )
    acceptance_criteria = tasks.get("acceptance_criteria") or []
    prompt = f"""Task ID: {tasks.get("id")}
        Status: {tasks.get("status")}
        Instructions: {tasks.get("content")}
        Target file: {target_file}
        Acceptance criteria: {", ".join(acceptance_criteria) if acceptance_criteria else "none specified - use the instructions as the criteria"}
        Project root: {PROJECT_ROOT}
        {f"Context from previous steps:\n{context}" if context else ""}"""

    messages = [
        {
            "role": "system",
            "content": (
                """You are a developer agent operating in a task loop controlled by an orchestrator.

INPUT: You will receive a task with: task_id, description, status, target_file (path, may or may not exist),
acceptance_criteria (list of conditions that define "done"), and project_root (the absolute path you must
stay inside for every read/write/execute/command).

TOOLS:
- read_file(path) - read an existing file
- write_file(path, content) - write a file to the current path
- code_execution(path) - runs an existing file to check it executes/imports cleanly
- run_command(command) - runs a shell command in the project root (ls, mkdir, python -m venv, pip install,
  pytest, etc.) - this is also how you inspect directories; there is no separate list_dir tool.

WORKFLOW:
1. Discovery (ONE command total for this task): run a single `run_command("ls ...")` (or read a single file)
   to check whether a relevant folder/file already exists under the project root and whether any similarly
   named folder already covers this task. Do this once, before your first write. Do not re-check state you
   have already observed unless a write_file/run_command just changed it.
2. If a relevant folder does not exist and target_file gives no directory hint, create one whose name is
   directly derived from the task instructions or target_file path - do not invent an unrelated name.
3. If target_file exists -> call read_file first. Modify ONLY the code relevant to the task description.
   Do not refactor unrelated code, change formatting/imports not tied to the task, or touch other files.
4. If target_file does not exist -> create it via write_file with minimal necessary content to satisfy
   acceptance_criteria.
5. After every write_file call to a file with executable logic, run code_execution on that file to validate
   it runs/imports cleanly. Use run_command instead for project-level setup (directories, venv, installing
   dependencies, running test suites).
6. If code_execution errors: read the traceback, patch the specific issue via write_file, re-run.
   Max 3 fix attempts per task. If unresolved after 3 attempts -> stop, do not keep looping; report status
   "failed" with the error.
7. Once the task is satisfied (or unresolved after 3 fix attempts), respond with plain text (no tool call)
   containing ONLY the final JSON described below. This is how the orchestrator knows you are done.

LOOP SAFETY (enforced by the orchestrator, not just you):
There is no fixed limit on how many tool calls you may make - keep working until the task is genuinely done
or genuinely blocked. However, the orchestrator will forcibly abort this task as "failed" if you call the
exact same tool with the exact same arguments 3 times in a row, or if a tool keeps returning the same result
3 times in a row despite you varying the arguments. Both are signs you are stuck rather than making progress.
If a call or read fails or is unclear, change your approach (different path, smaller diff, re-read the exact
error) rather than repeating the same action hoping for a different result.

RETURN FORMAT:
Your final message must contain ONLY the raw JSON object below - no markdown fences, no leading or trailing
prose, no explanation. This is machine-parsed.
{
  "task_id": "<id>",
  "status": "completed" | "failed",
  "files_changed": ["path1", ...],
  "summary": "<1-2 sentence description of what changed>",
  "execution_output": "<last code_execution stdout/stderr>",
  "error": "<null, or reason if status is failed>"
}

CONSTRAINTS:
- Do not read/write/execute outside the project_root given above.
- Do not install new dependencies unless explicitly permitted in the task; if a missing-package error blocks
  execution, report it in "error" rather than installing silently.
- Never guess at ambiguous requirements - if acceptance_criteria conflicts with existing code, return status
  "failed" with a clear error explaining the conflict instead of proceeding.
- Skip code_execution for files with no executable logic (empty files, __init__.py with no content, static
  text like README.md). Only run code_execution on files containing actual Python logic."""
            ),
        },
        {"role": "user", "content": prompt},
    ]

    final_status = "failed"
    final_output = None

    last_call_sig = None
    call_repeat = 0
    last_result_sig = None
    result_repeat = 0

    iteration = 0
    while True:
        iteration += 1
        response = client.chat.completions.create(
            model=Model,
            messages=messages,
            tools=tools,
            temperature=0.1,
        )
        msg = response.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            # Model produced its final answer with no further tool calls.
            final_output = msg.content
            final_status = _extract_status(msg.content)
            break

        print(f"[iteration {iteration}] tool calls:", msg.tool_calls)

        stuck = False
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            args_str = (
                tc.function.arguments
            )  # raw string; stable for signature comparison

            # --- call-signature loop check: same tool + same args, back to back ---
            call_sig = (fn_name, args_str)
            if call_sig == last_call_sig:
                call_repeat += 1
            else:
                call_repeat = 1
                last_call_sig = call_sig

            if call_repeat >= MAX_REPEAT_CALLS:
                stuck = True
                final_status = "failed"
                final_output = json.dumps(
                    {
                        "task_id": tasks.get("id"),
                        "status": "failed",
                        "files_changed": [],
                        "summary": "Aborted: same tool call repeated without progress.",
                        "execution_output": None,
                        "error": (
                            f"'{fn_name}' called with identical arguments {MAX_REPEAT_CALLS}x "
                            "consecutively - stuck loop detected."
                        ),
                    }
                )
                break

            # --- execute the tool ---
            try:
                args = json.loads(args_str)
                result = TOOL_IMPL[fn_name](**args)
                print("result", result)
            except Exception as e:
                result = f"ERROR calling {fn_name}: {e}"

            # --- result-signature loop check: same tool + same result, back to back ---
            result_sig = (fn_name, hashlib.md5(str(result).encode()).hexdigest())
            if result_sig == last_result_sig:
                result_repeat += 1
            else:
                result_repeat = 1
                last_result_sig = result_sig

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(result),
                }
            )

            if result_repeat >= MAX_REPEAT_RESULTS:
                stuck = True
                final_status = "failed"
                final_output = json.dumps(
                    {
                        "task_id": tasks.get("id"),
                        "status": "failed",
                        "files_changed": [],
                        "summary": "Aborted: tool keeps returning the same result despite varying arguments.",
                        "execution_output": str(result)[:500],
                        "error": (
                            f"'{fn_name}' returned an identical result {MAX_REPEAT_RESULTS}x in a row - "
                            "no progress being made."
                        ),
                    }
                )
                break

        if stuck:
            break

    return final_status, final_output


def _extract_status(content: str) -> str:
    """Parse the model's final JSON reply to get its actual status,
    falling back to 'failed' if content isn't valid/parseable JSON."""
    if not content:
        return "failed"
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[1] if "\n" in text else text
        text = text.removesuffix("json").strip()
    try:
        parsed = json.loads(text)
        return parsed.get("status", "failed")
    except (json.JSONDecodeError, AttributeError):
        return "failed"
