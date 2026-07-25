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
            "content": """You are a planner. Given a user request, output ONLY the todo list.No other text.
            When you get the tasks {tasks}, break it down into smaller doable items and call update_todos
            to create the initial list (status 'pending'). As you start an item call update_todos with it set
            to 'in_progress', and when finished call update_todos with it set to 'completed'. Always resend the
            full list on every call. Always respond with valid JSON only.
            The todo full list should be in this format
            [{id:1,content:"",status:"pending/in_progress/completed"},{id:2,content:"",status:"pending/in_progress/completed"}]""",
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


if "todos" in data:
    result = data.get("todos")
else:
    result = data

current_todos = []
context = ""
for task in range(len(result)):
    # print(result[task]['task'])
    # print(f"task {task},{result[task]['content']}")
    router = client.chat.completions.create(
        model=Model,
        messages=[
            {
                "role": "system",
                "content": "You are a router. Given a user request, output ONLY the name of the best agent "
                f"from this list: {list(AGENTS.keys())}. No other text.",
            },
            {"role": "user", "content": result[task]["content"]},
        ],
        temperature=0.1,
    )
    task_prompt = (
        f"{result[task]['content']}\n\nContext from previous steps:\n{context}"
        if context
        else result[task]["content"]
    )

    print("calling the Agent:", router.choices[0].message.content)
    print('Task:',task_prompt)
    agent_name = router.choices[0].message.content.strip()
    if agent_name == "Developer":
        status, output = developer(task_prompt)
    elif agent_name == "QA Engineer":
        status, output = qa_engineer(task_prompt)
    else:
        print("another agent")
        continue
    context += f"\n[{agent_name}] {output}"
