import json
from openai import OpenAI
import os
from tools import read_file, write_file, update_todos
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
            "name": "update_todos",
            "description": "Replace the current todo list. Call this to create the initial list and again every time an item's status changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "todos": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"},
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "completed"],
                                },
                            },
                            "required": ["content", "status"],
                        },
                    }
                },
                "required": ["todos"],
            },
        },
    },
]

TOOL_IMPL = {
    "read_file": read_file,
    "write_file": write_file,
    "update_todos": update_todos,
}


def qa_engineer(tasks: str, max_turns: int = 25) -> tuple[str, str]:
    client = OpenAI(base_url=MODEL_HOST, api_key=OPENAI_API_KEY)
    current_todos = []
    messages = [
        {
            "role": "system",
            "content": (
                "You are a developer. You will work on the tasks assigned by the orchestrator. "
                f"When you get the tasks {tasks}, break it down into smaller doable items and call update_todos "
                "to create the initial list (status 'pending'). As you start an item call update_todos with it set "
                "to 'in_progress', and when finished call update_todos with it set to 'completed'. Always resend the "
                "full list on every call. Use read_file/write_file for any actual file work the tasks require. "
                "Stop only when every item in the todo list is 'completed'."
            ),
        },
        {"role": "user", "content": tasks},
    ]

    for _ in range(max_turns):
        response = client.chat.completions.create(
            model=Model,
            messages=messages,
            tools=tools,
            temperature=0.1,
        )
        msg = response.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            if current_todos and any(t["status"] != "completed" for t in current_todos):
                pending = [t for t in current_todos if t["status"] != "completed"]
                messages.append(
                    {
                        "role": "user",
                        "content": f"You stopped without updating the todo list. These items are still not 'completed': {pending}. "
                        "If the work for any of them is already done, call update_todos right now to mark them 'completed'.",
                    }
                )
                continue
            return "completed", msg.content

        for call in msg.tool_calls:
            fn = TOOL_IMPL[call.function.name]
            args = json.loads(call.function.arguments)
            if call.function.name == "update_todos":
                current_todos = args["todos"]
            try:
                result = fn(**args)
            except Exception as e:
                result = f"ERROR: {e}"
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result),
                }
            )

    pending = [t for t in current_todos if t["status"] != "completed"]
    return "max_turns", msg.content
