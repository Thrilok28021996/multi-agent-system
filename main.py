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

MAX_QA_ROUNDS = 3  # dev-fix <-> re-test cycles allowed per task before giving up

parser = argparse.ArgumentParser(
    prog="Orchestrator",
    description="What the program does",
    epilog="Text at the bottom of help",
)
parser.add_argument("--query", "--q")
args = parser.parse_args()
client = OpenAI(
    base_url=MODEL_HOST,
    api_key=os.environ["OMNIROUTE_API_KEY"],  # required but ignored
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
result = data["todos"]
current_todos = result  # keep a live reference to the todo list
context = ""


def _extract_qa_feedback(qa_output: str) -> str:
    """Pull the actionable bits out of QA's JSON so the developer gets a
    focused fix instruction instead of the whole raw payload."""
    try:
        text = qa_output.strip()
        if text.startswith("```"):
            text = text.strip("`")
            text = text.split("\n", 1)[1] if "\n" in text else text
            text = text.removesuffix("json").strip()
        parsed = json.loads(text)
        return (
            f"Summary: {parsed.get('summary')}\n"
            f"Tests failed: {parsed.get('tests_failed')}\n"
            f"Error/root cause: {parsed.get('error')}\n"
            f"Execution output: {parsed.get('execution_output')}"
        )
    except (json.JSONDecodeError, AttributeError):
        return qa_output  # fall back to raw text if QA didn't return clean JSON


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
    agent_name = router.choices[0].message.content.strip()
    print("calling the Agent:", agent_name)
    print("Task:", task_data)

    if agent_name == "Developer":
        status, output = developer(task_data, context=context)
    elif agent_name == "QA Engineer":
        status, output = qa_engineer(task_data, context=context)
    else:
        print("another agent")
        task_data["status"] = "skipped"
        continue

    print("*" * 30)

    # --- QA <-> Developer feedback loop ---
    # If QA ran and failed, send its findings straight back to the developer
    # (bypassing the router, since this is a known fix cycle, not a fresh
    # routing decision) and re-test, up to MAX_QA_ROUNDS times.
    if agent_name == "QA Engineer" and status == "failed":
        qa_round = 1
        while status == "failed" and qa_round <= MAX_QA_ROUNDS:
            qa_feedback = _extract_qa_feedback(output)
            print(f"QA round {qa_round} failed, sending feedback to Developer:")
            print(qa_feedback)

            fix_context = (
                context
                + f"\nQA found issues on attempt {qa_round}. Fix ONLY what QA "
                f"reported, do not touch unrelated code:\n{qa_feedback}"
            )
            dev_status, dev_output = developer(task_data, context=fix_context)
            context += f"\n[Developer fix round {qa_round}] Task {task_data['id']} ({dev_status}): {dev_output}"

            if dev_status != "completed":
                # Developer couldn't even complete the fix — stop retrying.
                status, output = dev_status, dev_output
                agent_name = "Developer"
                break

            # Re-test after the fix.
            qa_status, qa_output = qa_engineer(task_data, context=dev_output)
            context += f"\n[QA re-test round {qa_round}] Task {task_data['id']} ({qa_status}): {qa_output}"
            status, output = qa_status, qa_output
            agent_name = "QA Engineer"
            qa_round += 1

        if status == "failed":
            print(f"QA still failing after {MAX_QA_ROUNDS} developer fix rounds.")

    task_data["status"] = "completed" if status == "completed" else "failed"
    print("Status:", task_data)
    context += (
        f"\n[{agent_name}] Task {task_data['id']} ({task_data['status']}): {output}"
    )

print("\nFinal todo list:")
print(json.dumps(current_todos, indent=2))
