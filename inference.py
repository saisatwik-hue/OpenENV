"""
inference.py — OpenEnv: Email Triage & Response
Baseline inference script for Phase 2 deep validation.

Structured output format (required):
  [START] task=TASK_NAME
  [STEP]  step=N reward=R action=ACTION email=EMAIL_ID
  [END]   task=TASK_NAME score=S steps=N
"""

import os
import sys
import json
import asyncio
import argparse

# ── Environment variables (EXACTLY as required by validator) ──────────────────
# Defaults set ONLY for API_BASE_URL and MODEL_NAME — NOT for HF_TOKEN
API_BASE_URL     = os.getenv("API_BASE_URL", "<your-active-endpoint>")
MODEL_NAME       = os.getenv("MODEL_NAME",   "<your-active-model>")
HF_TOKEN         = os.getenv("HF_TOKEN")           # NO default — required by checklist

# Optional — used only when calling from_docker_image()
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

# ── Structured output (REQUIRED — printed to stdout with flush=True) ──────────
def log_start(task_name: str):
    print(f"[START] task={task_name}", flush=True)

def log_step(step: int, reward: float, action: str, email_id: str):
    print(f"[STEP] step={step} reward={round(reward, 4)} action={action} email={email_id}", flush=True)

def log_end(task_name: str, score: float, steps: int):
    # Clamp strictly between 0 and 1 exclusive as required by validator
    clamped = max(0.0001, min(0.9999, float(score)))
    print(f"[END] task={task_name} score={round(clamped, 4)} steps={steps}", flush=True)

# ── OpenAI client (REQUIRED — configured via API_BASE_URL + HF_TOKEN) ─────────
def get_openai_client():
    """Build OpenAI client using API_BASE_URL and HF_TOKEN as required."""
    try:
        from openai import OpenAI
        return OpenAI(
            base_url=API_BASE_URL,
            api_key=HF_TOKEN if HF_TOKEN else "no-token",
        )
    except ImportError:
        return None

def call_llm(client, messages: list) -> str:
    """Call LLM via OpenAI client configured through API_BASE_URL + HF_TOKEN."""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.1,
            max_tokens=400,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"action_type": "archive", "email_id": "unknown", "error": str(e)})

def parse_action(text: str, email_id: str) -> dict:
    try:
        action = json.loads(text)
        if "email_id"    not in action: action["email_id"]    = email_id
        if "action_type" not in action: action["action_type"] = "archive"
        return action
    except Exception:
        return {"action_type": "archive", "email_id": email_id}

# ── Heuristic fallback (used when HF_TOKEN not set or LLM unavailable) ────────
def priority_score(email: dict) -> float:
    subject = email.get("subject", "").lower()
    sender  = email.get("sender",  "").lower()
    score   = 0.5

    if any(w in subject for w in ["critical","p0","down","breach","gdpr","security","ssl","expired","outage"]):
        score = 0.97
    elif any(w in subject for w in ["urgent","asap","deadline","board","legal","hipaa","aws bill"]):
        score = 0.82
    elif any(w in subject for w in ["complaint","dispute","churn","billing","renewal"]):
        score = 0.70
    elif any(w in subject for w in ["newsletter","lunch","cafeteria","reminder","digest"]):
        score = 0.06

    if any(w in sender for w in ["promo","domains-r","crypto","paypa1","reward"]):
        score = 0.0

    score += email.get("thread_depth", 0) * 0.03
    return min(1.0, max(0.0, score))

def heuristic_action(email: dict) -> dict:
    pri  = priority_score(email)
    subj = email.get("subject", "").lower()
    eid  = email["id"]

    if any(w in email.get("sender","").lower() for w in ["promo","crypto","paypa1","reward"]):
        return {"action_type":"archive","email_id":eid,"category":"spam","priority_score":0.0}

    if pri >= 0.95:
        targets = {"pagerduty":"backend-oncall","security":"security-team","aws":"cloud-ops",
                   "ssl":"devops","gdpr":"legal-compliance","payment":"engineering-lead"}
        target = next((t for k,t in targets.items() if k in subj), "oncall")
        return {"action_type":"escalate","email_id":eid,"category":"urgent",
                "priority_score":pri,"escalate_to":target}

    if pri >= 0.80:
        return {"action_type":"respond","email_id":eid,"category":"urgent","priority_score":pri,
                "response_text":"Reviewing this urgent matter immediately. Will take decisive action within the hour."}

    if pri >= 0.45:
        return {"action_type":"respond","email_id":eid,"category":"normal","priority_score":pri,
                "response_text":"Thank you for your email. I will address this promptly and follow up shortly."}

    if pri >= 0.15:
        return {"action_type":"triage","email_id":eid,"category":"low","priority_score":pri}

    return {"action_type":"archive","email_id":eid,"category":"low","priority_score":pri}

# ── Run one full episode ───────────────────────────────────────────────────────
async def run_task(task_id: str, base_url: str) -> dict:
    try:
        import httpx
    except ImportError:
        print("[ERROR] httpx not installed — run: pip install httpx", flush=True)
        log_start(task_id)
        log_end(task_id, 0.0, 0)
        return {"task_id": task_id, "score": 0.0}

    client     = get_openai_client()
    use_llm    = bool(HF_TOKEN and client)

    log_start(task_id)

    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=30) as http:

            # Reset
            r = await http.post(f"/reset?task_id={task_id}")
            if r.status_code != 200:
                print(f"[ERROR] /reset failed {r.status_code}", flush=True)
                log_end(task_id, 0.0, 0)
                return {"task_id": task_id, "score": 0.0}

            obs       = r.json()["observation"]
            inbox     = obs.get("inbox", [])
            max_steps = obs.get("context", {}).get("max_steps", 55)
            processed = set()
            step_num  = 0

            # Episode loop
            while step_num < max_steps + 5:
                pending = [e for e in inbox if e["id"] not in processed]
                if not pending:
                    break

                email = sorted(pending, key=priority_score, reverse=True)[0]

                if use_llm:
                    body = obs.get("current_email_body", email.get("preview", ""))
                    msgs = [
                        {"role":"system","content":"You are an enterprise email manager. Output JSON only."},
                        {"role":"user","content":(
                            f"Email ID: {email['id']}\n"
                            f"Subject: {email['subject']}\n"
                            f"From: {email['sender']}\n"
                            f"Body: {body[:300]}\n\n"
                            "Return JSON: action_type, email_id, category, priority_score, "
                            "response_text, escalate_to, reason"
                        )}
                    ]
                    text   = call_llm(client, msgs)
                    action = parse_action(text, email["id"])
                else:
                    action = heuristic_action(email)

                processed.add(email["id"])
                step_num += 1

                sr = await http.post(f"/step?task_id={task_id}", json=action)
                if sr.status_code != 200:
                    log_step(step_num, 0.0, action.get("action_type","?"), email["id"])
                    continue

                result = sr.json()
                obs    = result["observation"]
                reward = result["reward"]
                done   = result["done"]

                log_step(step_num, reward, action.get("action_type","?"), email["id"])

                if done:
                    break

            # Grade
            gr = await http.post(f"/grader?task_id={task_id}")
            if gr.status_code != 200:
                log_end(task_id, 0.0, step_num)
                return {"task_id": task_id, "score": 0.0}

            grade = gr.json()
            score = grade.get("episode_score", 0.0)
            log_end(task_id, score, step_num)

            return {"task_id": task_id, "score": score,
                    "passed": grade.get("passed", False), "steps": step_num}

    except Exception as e:
        print(f"[ERROR] {task_id}: {e}", flush=True)
        log_end(task_id, 0.0, 0)
        return {"task_id": task_id, "score": 0.0}

# ── Main ───────────────────────────────────────────────────────────────────────
async def run_all(task_filter: str, base_url: str) -> dict:
    tasks = ["task_1", "task_2", "task_3"]
    if task_filter != "all":
        tasks = [task_filter]

    print(f"[INFO] OpenEnv Email Triage — Baseline Inference", flush=True)
    print(f"[INFO] API_BASE_URL={API_BASE_URL}", flush=True)
    print(f"[INFO] MODEL_NAME={MODEL_NAME}", flush=True)
    print(f"[INFO] HF_TOKEN={'set' if HF_TOKEN else 'not set — using heuristic agent'}", flush=True)
    print(f"[INFO] ENV_SERVER={base_url}", flush=True)
    print(f"[INFO] Tasks={','.join(tasks)}", flush=True)

    results = {}
    for task_id in tasks:
        results[task_id] = await run_task(task_id, base_url)

    scores = [r["score"] for r in results.values() if isinstance(r.get("score"), float)]
    avg    = round(sum(scores) / len(scores), 4) if scores else 0.0

    print(f"[SUMMARY] average_score={avg} tasks_run={len(tasks)}", flush=True)
    results["average_score"] = avg
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenEnv Email Triage Inference")
    parser.add_argument("--task",   default="all",                  help="task_1 / task_2 / task_3 / all")
    parser.add_argument("--server", default="http://localhost:7860", help="Environment server base URL")
    args = parser.parse_args()

    asyncio.run(run_all(args.task, args.server))
