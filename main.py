### Orchestration - where the llm that is good at instruction following will call
### the respective agent accordingly

from dotenv import load_dotenv
import os
import json

load_dotenv()
Model = os.getenv("MODEL")
MODEL_HOST = os.getenv("MODEL_HOST")
OPENAI_API_KEY = os.getenv("BACKEND")

from openai import OpenAI
import argparse
from agents.developer import developer
from agents.qa_engineer import qa_engineer

parser = argparse.ArgumentParser(
    prog="Orchestrator",
    description="What the program does",
    epilog="Text at the bottom of help",
)
parser.add_argument("--query", "--q")
args = parser.parse_args()


client = OpenAI(
    base_url=MODEL_HOST,
    api_key=OPENAI_API_KEY,  # required but ignored
)


AGENTS = {"Developer": developer, "QA Engineer": qa_engineer}

planner = client.chat.completions.create(
    model=Model,
    messages=[
        {
            "role": "system",
            "content": """You are a planner. Given a user request, break it down into a sequence of
small, concrete, actionable tasks and output ONLY a JSON object — no other text.

Format (valid JSON, all keys quoted):
{
  "todos": [
    {
      "id": 1,
      "content": "Short imperative description of the task",
      "status": "pending",
      "target_file": "relative/path/if/known, or null",
      "acceptance_criteria": ["condition 1", "condition 2"]
    }
  ]
}

Rules:
- Every task's status is always "pending" — do not use any other status value.
- Order tasks so dependencies come before the tasks that need them.
- target_file should be a real relative path when you can infer one, otherwise null.
- acceptance_criteria should be a short list of concrete, checkable conditions; use an empty list if none apply.
- Output valid JSON only.""",
        },
        {"role": "user", "content": args.query},
    ],
    temperature=0.1,
    response_format={"type": "json_object"},
)

raw = planner.choices[0].message.content.strip()

# strip accidental code fences if the model adds them anyway
if raw.startswith("```"):
    raw = raw.strip("`")
    raw = raw.split("\n", 1)[1] if "\n" in raw else raw
    raw = raw.removesuffix("json").strip()

data = json.loads(raw)

data = json.loads(raw)
result = data["todos"]
# if "todos" in data:
#     result = data.get("todos")
# else:
#     result = data

current_todos = result  # keep a live reference to the todo list
context = ""
for task in range(len(result)):
    task_data = current_todos[task]
    task_data["status"] = "in_progress"

    router = client.chat.completions.create(
        model=Model,
        messages=[
            {
                "role": "system",
                "content": "You are a router. Given a user request, output ONLY the name of the best agent "
                f"from this list: {list(AGENTS.keys())}. No other text.",
            },
            {"role": "user", "content": task_data["content"]},
        ],
        temperature=0.1,
    )

    print("calling the Agent:", router.choices[0].message.content)
    print("Task:", task_data)
    agent_name = router.choices[0].message.content.strip()

    if agent_name == "Developer":
        status, output = developer(task_data, context=context)
    elif agent_name == "QA Engineer":
        status, output = qa_engineer(task_data, context=context)
    else:
        print("another agent")
        task_data["status"] = "skipped"
        continue

    task_data["status"] = "completed" if status == "completed" else "failed"
    context += (
        f"\n[{agent_name}] Task {task_data['id']} ({task_data['status']}): {output}"
    )

print("\nFinal todo list:")
print(json.dumps(current_todos, indent=2))
