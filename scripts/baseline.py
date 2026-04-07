"""Baseline inference script — OpenAI API against all 3 tasks."""
import os, json, asyncio
import httpx

BASE_URL = os.environ.get("ENV_BASE_URL", "http://localhost:7860")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL = os.environ.get("BASELINE_MODEL", "gpt-4o-mini")

SYSTEM = """You are an expert email manager AI agent. Process emails by:
1. Correct category: urgent/normal/low/spam/internal/external
2. Accurate priority 0.0-1.0
3. Right action: triage/respond/escalate/archive/flag/skip
4. Quality responses when needed

RULES: Urgent/security/legal → escalate first. Spam → archive. Premium customers with issues → respond with empathy and resolution. Always output valid JSON only."""

async def call_llm(messages):
    if not OPENAI_API_KEY:
        return json.dumps({"action_type": "archive", "email_id": "unknown"})
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{OPENAI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={"model": MODEL, "messages": messages, "temperature": 0.1,
                  "max_tokens": 500, "response_format": {"type": "json_object"}})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

def parse_action(text, email_id):
    try:
        a = json.loads(text)
        if "email_id" not in a: a["email_id"] = email_id
        if "action_type" not in a: a["action_type"] = "archive"
        return a
    except: return {"action_type": "archive", "email_id": email_id}

def priority_heuristic(email):
    s = email.get("subject","").lower(); sn = email.get("sender","").lower()
    score = 0.5
    if any(w in s for w in ["critical","p0","down","breach","security","expired","gdpr"]): score=0.95
    elif any(w in s for w in ["urgent","asap","today","deadline","final","board","legal","aws bill"]): score=0.80
    elif any(w in s for w in ["complaint","dispute","churn","billing","renewal","nps"]): score=0.70
    elif any(w in s for w in ["newsletter","lunch","cafeteria","reminder","digest","offer"]): score=0.05
    if any(w in sn for w in ["pagerduty","promo","domains-r","crypto","paypa1"]): score=0.0
    score += email.get("thread_depth",0)*0.03
    return min(1.0,max(0.0,score))

async def run_task(task_id):
    print(f"\n{'='*55}\nTask: {task_id}\n{'='*55}")
    if not OPENAI_API_KEY:
        return {"task_id": task_id, "score": 0.0, "error": "OPENAI_API_KEY not set"}
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as c:
        obs = (await c.post(f"/reset?task_id={task_id}")).json()["observation"]
        print(f"Emails: {len(obs['inbox'])} | Max steps: {obs['context']['max_steps']}")
        processed = set(); step = 0
        while step < obs['context']['max_steps'] + 2:
            pending = [e for e in obs['inbox'] if e['id'] not in processed]
            if not pending: break
            email = sorted(pending, key=lambda e: priority_heuristic(e), reverse=True)[0]
            body = obs.get('current_email_body','') if obs.get('current_email',{}) and obs['current_email']['id']==email['id'] else email.get('preview','')
            msg = [{"role":"system","content":SYSTEM},
                   {"role":"user","content":f"Task: {obs['task_description'][:120]}\n\nEmail:\nID: {email['id']}\nSubject: {email['subject']}\nFrom: {email['sender']}\nBody: {body[:400]}\n\nOutput JSON action for email_id: {email['id']}"}]
            llm = await call_llm(msg); action = parse_action(llm, email['id'])
            processed.add(email['id'])
            sr = await c.post(f"/step?task_id={task_id}", json=action)
            if sr.status_code != 200: step+=1; continue
            sd = sr.json(); obs = sd['observation']; step+=1
            print(f"  [{email['id']}] {action.get('action_type')} cat={action.get('category')} pri={action.get('priority_score')} r={sd['reward']:+.3f}")
            if sd['done']: break
        grade = (await c.post(f"/grader?task_id={task_id}")).json()
        print(f"\n  Score: {grade['episode_score']:.4f} | {'PASSED' if grade['passed'] else 'FAILED'} | {grade['summary']}")
        return {"task_id": task_id, "score": grade['episode_score'], "passed": grade['passed'], "breakdown": grade.get('breakdown',{})}

async def run_baseline_all():
    if not OPENAI_API_KEY:
        return {"task_1":{"score":0.0,"error":"No API key"},"task_2":{"score":0.0,"error":"No API key"},"task_3":{"score":0.0,"error":"No API key"},"model":MODEL,"note":"Set OPENAI_API_KEY"}
    results = {}
    for tid in ["task_1","task_2","task_3"]:
        try: results[tid] = await run_task(tid)
        except Exception as e: results[tid] = {"score":0.0,"error":str(e)}
    scores = [r["score"] for r in results.values() if "error" not in r]
    results["average_score"] = round(sum(scores)/len(scores),4) if scores else 0.0
    results["model"] = MODEL
    print(f"\n{'='*55}\nBASELINE SUMMARY\n{'='*55}")
    for t in ["task_1","task_2","task_3"]: print(f"  {t}: {results[t].get('score',0):.4f} {'✅' if results[t].get('passed') else '❌'}")
    print(f"  Average: {results['average_score']:.4f} | Model: {MODEL}")
    return results

if __name__ == "__main__":
    asyncio.run(run_baseline_all())
