import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import re


load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL = "gpt-5.4-nano-2026-03-17"


# Questions where the answer is a legal or personal declaration: a human must answer
ASK_PATTERNS = [
    r"sanction", r"export control", r"authori[sz]ed to work", r"work authori[sz]ation",
    r"sponsorship", r"\bvisa\b", r"citizen", r"\bresident", r"criminal", r"convict",
    r"salary", r"relocat",
]

# Voluntary self-identification: leave blank by default
SKIP_PATTERNS = [
    r"\bgender\b", r"hispanic", r"latino", r"\brace\b", r"ethnic", r"veteran",
    r"disabilit", r"pronoun", r"sexual orientation",
]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def safety_check(q):
    """Return (action, reason) if this question is handled by a hard rule, else None."""
    # Look at the question and, for groups, the option labels too
    text = (q["question"] + " " + " ".join(o["label"] for o in q.get("options", []))).lower()

    if any(re.search(p, text) for p in ASK_PATTERNS):
        return "ask_human", "legal, work-rights or sensitive question"

    if any(re.search(p, text) for p in SKIP_PATTERNS):
        if q["required"]:
            return "ask_human", "self-identification question, but the form requires an answer"
        return "skip", "voluntary self-identification"

    return None

SYSTEM_PROMPT = """You help fill in a job application form for a candidate.
You get the candidate's profile and a numbered list of form questions.
Return JSON: {"plan": [{"n": <question number>, "action": "fill" | "ask_human" | "skip", "value": "<text or empty>", "reason": "<short>"}]}

Rules:
- Only use facts that are in the profile. Never invent or guess anything.
- Questions can be worded differently from the profile keys ("Forename" means first_name).
- If the answer is in the profile: action "fill" with that exact value.
- If the answer is NOT in the profile and the question is required: "ask_human".
- If the answer is NOT in the profile and the question is optional: "skip".
- For a resume file upload: action "fill" with value "@resume". Skip any other optional file upload.
- Give exactly one entry per question number."""


def ask_llm(profile, questions):
    """Send the profile and the questions to the LLM and return its plan (a list)."""
    numbered = [
        {
            "n": n,
            "question": q["question"],
            "type": q["type"],
            "required": q["required"],
            "id": q.get("id"),
        }
        for n, q in enumerate(questions)
    ]
    user_message = json.dumps({"profile": profile, "questions": numbered}, indent=2)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)["plan"]


def clean_plan(raw_plan, questions):
    """Check the LLM's answer. Anything missing or invalid becomes ask_human."""
    by_n = {item.get("n"): item for item in raw_plan}
    plan = []
    for n, q in enumerate(questions):
        item = by_n.get(n)
        if not item or item.get("action") not in ("fill", "ask_human", "skip"):
            plan.append({"question": q["question"], "type": q["type"], "id": q.get("id"), "action": "ask_human",
                         "value": "", "reason": "LLM gave no valid answer"})
        else:
            plan.append({"question": q["question"], "type": q["type"], "id": q.get("id"), "action": item["action"],
                         "value": item.get("value", ""), "reason": item.get("reason", "")})
    return plan

if __name__ == "__main__":
    questions = load_json("form_questions.json")

    decided = []   # settled by the hard rules
    for_llm = []   # everything else, for the LLM later

    for q in questions:
        result = safety_check(q)
        if result:
            decided.append({
                "question": q["question"],
                "type": q["type"],
                "id": q.get("id"),
                "value": "",
                "action": result[0],
                "reason": result[1],
            })
        else:
            for_llm.append(q)

    """print(f"{len(decided)} questions settled by safety rules, {len(for_llm)} left for the LLM\n")
    for d in decided:
        print(f"[{d['action']}] {d['question'][:250]}")"""
        
    profile = load_json("profile.json")
    llm_plan = clean_plan(ask_llm(profile, for_llm), for_llm)

    final_plan = decided + llm_plan
    with open("plan.json", "w", encoding="utf-8") as out:
        json.dump(final_plan, out, indent=2, ensure_ascii=False)

    for item in final_plan:
        print(f"[{item['action']}] {item['question'][:200]} -> {item['value']}")