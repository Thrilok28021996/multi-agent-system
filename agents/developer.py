import json
from openai import OpenAI
import os
from tools import read_file, write_file,code_execution
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

]

TOOL_IMPL = {
    "read_file": read_file,
    "write_file": write_file,
    "code_execution":code_execution,
}


def developer(tasks: str) -> tuple[str, str]:
    client = OpenAI(base_url=MODEL_HOST, api_key=OPENAI_API_KEY)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a developer. You will work on the tasks assigned by the orchestrator by using the respective tools(read_file,write_file) to read/write a file as necessary.if a file exists read that file and make only relevant changes to that file. Run code using the code_exection tool and fix any errors if found. Once the task has been completed. you will return the status as 'completed' "
            ),
        },
        {"role": "user", "content": tasks},
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
