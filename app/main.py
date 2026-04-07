from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn, os

from app.environment import EmailTriageEnv
from app.models import Action, StepResponse, ResetResponse, StateResponse
from app.tasks.registry import TASK_REGISTRY

app = FastAPI(title="OpenEnv: Email Triage — Peak Edition", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_envs: dict[str, EmailTriageEnv] = {}

def get_env(task_id="task_1"):
    if task_id not in _envs:
        _envs[task_id] = EmailTriageEnv(task_id=task_id)
    return _envs[task_id]

@app.post("/reset", response_model=ResetResponse, tags=["OpenEnv"])
async def reset(task_id: str = "task_1"):
    env = get_env(task_id); obs = env.reset()
    return ResetResponse(observation=obs, task_id=task_id)

@app.post("/step", response_model=StepResponse, tags=["OpenEnv"])
async def step(action: Action, task_id: str = "task_1"):
    env = get_env(task_id)
    if not env.started: raise HTTPException(400, "Call /reset first")
    obs, reward, done, info = env.step(action)
    return StepResponse(observation=obs, reward=reward, done=done, info=info)

@app.get("/state", response_model=StateResponse, tags=["OpenEnv"])
async def state(task_id: str = "task_1"):
    return StateResponse(state=get_env(task_id).state())

@app.get("/tasks", response_class=HTMLResponse, tags=["Extended"])
async def list_tasks(fmt: str = "html"):
    tasks_data = []
    for tid, tcls in TASK_REGISTRY.items():
        t = tcls()
        tasks_data.append({
            "task_id": tid, "name": t.name, "description": t.description,
            "difficulty": t.difficulty, "max_steps": t.max_steps,
            "email_count": len(t.get_emails()),
            "pass_threshold": t.pass_threshold,
            "action_schema": {
                "type": "object", "required": ["action_type", "email_id"],
                "properties": {
                    "action_type": {"type": "string", "enum": ["triage","respond","escalate","archive","flag","compose","skip"]},
                    "email_id": {"type": "string"},
                    "category": {"type": "string", "enum": ["urgent","normal","low","spam","internal","external"]},
                    "response_text": {"type": "string"},
                    "priority_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "reason": {"type": "string"},
                    "escalate_to": {"type": "string"},
                }
            }
        })
    if fmt == "json":
        from fastapi.responses import JSONResponse
        return JSONResponse({"tasks": tasks_data, "count": len(tasks_data)})

    diff_color = {"easy": "#22d75e", "medium": "#f97316", "hard": "#ef4444"}
    diff_bg    = {"easy": "rgba(34,215,94,.1)", "medium": "rgba(249,115,22,.1)", "hard": "rgba(239,68,68,.1)"}

    cards = ""
    for t in tasks_data:
        dc = diff_color.get(t["difficulty"], "#cdd6e8")
        db = diff_bg.get(t["difficulty"], "rgba(255,255,255,.05)")
        def _prop_html(k, v, req_fields):
            enum_span = ('<span class="prop-enum">' + " | ".join(v["enum"]) + "</span>") if "enum" in v else ""
            req_span  = '<span class="prop-req">required</span>' if k in req_fields else ""
            return (f'<div class="prop-row">'
                    f'<span class="prop-name">{k}</span>'
                    f'<span class="prop-type">{v.get("type","")}</span>'
                    + enum_span + req_span + '</div>')
        schema_props = "".join(
            _prop_html(k, v, t["action_schema"]["required"])
            for k, v in t["action_schema"]["properties"].items()
        )
        cards += f"""
        <div class="task-card">
          <div class="task-header">
            <div>
              <span class="task-id">{t["task_id"]}</span>
              <h2 class="task-name">{t["name"]}</h2>
            </div>
            <span class="diff-badge" style="color:{dc};background:{db}">{t["difficulty"].upper()}</span>
          </div>
          <p class="task-desc">{t["description"]}</p>
          <div class="task-meta-row">
            <div class="meta-pill">📧 {t["email_count"]} emails</div>
            <div class="meta-pill">⚡ {t["max_steps"]} max steps</div>
            <div class="meta-pill">🎯 Pass ≥ {int(t["pass_threshold"]*100)}%</div>
          </div>
          <div class="schema-block">
            <div class="schema-title">Action Schema</div>
            <div class="schema-required">Required: {" · ".join(t["action_schema"]["required"])}</div>
            <div class="props-list">{schema_props}</div>
          </div>
          <div class="task-footer">
            <a class="btn-primary" href="/?task={t['task_id']}">▶ Run in Dashboard</a>
            <a class="btn-secondary" href="/tasks?fmt=json">JSON</a>
          </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpenEnv · Tasks</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@700;800;900&display=swap" rel="stylesheet">
<style>
:root{{--bg:#05080d;--s1:#0a0f18;--s2:#0f1620;--b1:#1a2438;--ac:#00e5ff;--t:#cdd6e8;--m:#5a6a84;--mono:'JetBrains Mono',monospace;--sans:'Syne',sans-serif;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--t);font-family:var(--mono);min-height:100vh;}}
body::before{{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(0,229,255,.018) 1px,transparent 1px),linear-gradient(90deg,rgba(0,229,255,.018) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;}}
.topbar{{height:52px;background:var(--s1);border-bottom:1px solid var(--b1);display:flex;align-items:center;padding:0 28px;gap:14px;position:sticky;top:0;z-index:10;}}
.logo{{font-family:var(--sans);font-size:17px;font-weight:900;color:#fff;letter-spacing:-1px;display:flex;align-items:center;gap:9px;text-decoration:none;}}
.logo-box{{width:26px;height:26px;border:2px solid var(--ac);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:13px;color:var(--ac);box-shadow:0 0 10px rgba(0,229,255,.25);}}
.pill{{font-size:10px;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:.5px;text-transform:uppercase;background:rgba(0,229,255,.1);color:var(--ac);border:1px solid rgba(0,229,255,.2);}}
.nav-links{{margin-left:auto;display:flex;gap:20px;}}
.nav-links a{{color:var(--m);text-decoration:none;font-size:11px;transition:color .15s;}}
.nav-links a:hover{{color:var(--ac);}}
.nav-links a.active{{color:var(--ac);}}
.page{{max-width:1100px;margin:0 auto;padding:40px 24px;}}
.page-header{{margin-bottom:36px;}}
.page-title{{font-family:var(--sans);font-size:32px;font-weight:900;color:#fff;letter-spacing:-1px;margin-bottom:8px;}}
.page-sub{{color:var(--m);font-size:13px;line-height:1.7;max-width:640px;}}
.tasks-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px;}}
.task-card{{background:var(--s1);border:1px solid var(--b1);border-radius:12px;padding:24px;display:flex;flex-direction:column;gap:16px;transition:border-color .2s;}}
.task-card:hover{{border-color:rgba(0,229,255,.2);}}
.task-header{{display:flex;justify-content:space-between;align-items:flex-start;}}
.task-id{{font-size:10px;font-weight:700;color:var(--m);text-transform:uppercase;letter-spacing:1px;display:block;margin-bottom:4px;}}
.task-name{{font-family:var(--sans);font-size:20px;font-weight:800;color:#fff;}}
.diff-badge{{font-size:10px;font-weight:700;padding:4px 12px;border-radius:20px;text-transform:uppercase;letter-spacing:.5px;flex-shrink:0;}}
.task-desc{{font-size:11.5px;color:var(--m);line-height:1.7;}}
.task-meta-row{{display:flex;gap:8px;flex-wrap:wrap;}}
.meta-pill{{font-size:10px;font-weight:600;padding:4px 10px;background:var(--s2);border:1px solid var(--b1);border-radius:20px;color:var(--t);}}
.schema-block{{background:var(--s2);border:1px solid var(--b1);border-radius:8px;padding:14px;}}
.schema-title{{font-size:9px;font-weight:700;color:var(--m);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;}}
.schema-required{{font-size:10px;color:var(--ac);margin-bottom:10px;}}
.props-list{{display:flex;flex-direction:column;gap:5px;}}
.prop-row{{display:flex;align-items:center;gap:8px;font-size:10px;}}
.prop-name{{color:#fff;font-weight:600;min-width:90px;}}
.prop-type{{color:#a78bfa;}}
.prop-enum{{color:var(--m);font-size:9.5px;}}
.prop-req{{color:var(--ac);font-size:9px;background:rgba(0,229,255,.08);padding:1px 6px;border-radius:3px;margin-left:auto;}}
.task-footer{{display:flex;gap:10px;margin-top:auto;}}
.btn-primary{{flex:1;padding:10px;background:rgba(0,229,255,.1);border:1px solid rgba(0,229,255,.25);border-radius:7px;color:var(--ac);font-family:var(--mono);font-size:11px;font-weight:700;text-align:center;text-decoration:none;transition:all .2s;}}
.btn-primary:hover{{background:rgba(0,229,255,.2);}}
.btn-secondary{{padding:10px 14px;background:transparent;border:1px solid var(--b1);border-radius:7px;color:var(--m);font-family:var(--mono);font-size:11px;text-decoration:none;transition:all .2s;}}
.btn-secondary:hover{{border-color:var(--ac);color:var(--ac);}}
</style>
</head>
<body>
<div class="topbar">
  <a href="/" class="logo"><div class="logo-box">✉</div>OpenEnv</a>
  <span class="pill">PEAK EDITION</span>
  <div class="nav-links">
    <a href="/">Dashboard</a>
    <a href="/tasks" class="active">Tasks</a>
    <a href="/health">Health</a>
    <a href="/docs">API Docs</a>
  </div>
</div>
<div class="page">
  <div class="page-header">
    <div class="page-title">Tasks</div>
    <p class="page-sub">3 tasks with progressive difficulty. Each defines a concrete email management objective with a programmatic grader that scores agent performance 0.0–1.0.</p>
  </div>
  <div class="tasks-grid">{cards}</div>
</div>
</body></html>"""


@app.post("/grader", tags=["Extended"])
async def grade(task_id: str = "task_1"):
    """Grade the current episode. Returns score 0.0-1.0 with full breakdown."""
    result = get_env(task_id).grade()
    # Enrich grader response with human-readable interpretation
    score = result.get("episode_score", 0.0)
    result["grade_letter"]   = "A" if score >= 0.90 else "B" if score >= 0.80 else "C" if score >= 0.70 else "D" if score >= 0.60 else "F"
    result["interpretation"] = (
        "Excellent — near-perfect email management" if score >= 0.90 else
        "Good — handles most emails correctly"      if score >= 0.80 else
        "Fair — correct on common cases"            if score >= 0.70 else
        "Poor — significant errors in triage"       if score >= 0.60 else
        "Failing — major issues with prioritisation"
    )
    result["reward_range"]   = {"min": -1.0, "max": 1.0, "shaped": True}
    result["scoring_notes"]  = {
        "task_1": "Category(40%) + Priority(30%) + Action(30%)",
        "task_2": "ActionType(20%) + Keywords(40%) + Completeness(20%) + Tone(20%)",
        "task_3": "Quality(30%) + Coverage(25%) + Prioritization(20%) + Critical(15%) + Efficiency(10%)"
    }.get(task_id, "See /tasks for details")
    return result

@app.post("/baseline", tags=["Extended"])
async def run_baseline():
    """Run baseline inference agent across all 3 tasks. Requires OPENAI_API_KEY env var."""
    from scripts.baseline import run_baseline_all
    return {"baseline_scores": await run_baseline_all()}

# ── Leaderboard ───────────────────────────────────────────────────────────────
_leaderboard: list[dict] = []

@app.post("/leaderboard/submit", tags=["Extended"])
async def leaderboard_submit(agent_name: str, task_id: str = "task_1"):
    """Submit your episode score to the leaderboard."""
    env = get_env(task_id)
    if not env.started:
        from fastapi import HTTPException
        raise HTTPException(400, "Run an episode first via /reset and /step")
    result = env.grade()
    entry = {
        "rank":       0,
        "agent":      agent_name,
        "task_id":    task_id,
        "score":      result["episode_score"],
        "passed":     result["passed"],
        "steps":      result["steps_taken"],
        "emails":     result["emails_processed"],
        "grade":      "A" if result["episode_score"] >= 0.90 else "B" if result["episode_score"] >= 0.80 else "C" if result["episode_score"] >= 0.70 else "D" if result["episode_score"] >= 0.60 else "F",
        "timestamp":  __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }
    _leaderboard.append(entry)
    _leaderboard.sort(key=lambda x: x["score"], reverse=True)
    for i, e in enumerate(_leaderboard):
        e["rank"] = i + 1
    return {"submitted": entry, "your_rank": entry["rank"], "total_entries": len(_leaderboard)}

@app.get("/leaderboard", tags=["Extended"])
async def get_leaderboard(task_id: str = "all", limit: int = 20):
    """View the episode score leaderboard."""
    entries = _leaderboard if task_id == "all" else [e for e in _leaderboard if e["task_id"] == task_id]
    return {
        "leaderboard": entries[:limit],
        "total":       len(entries),
        "task_filter": task_id,
        "note":        "Submit scores via POST /leaderboard/submit?agent_name=YourAgent&task_id=task_1",
    }

@app.get("/metrics", tags=["Extended"])
async def get_metrics(task_id: str = "task_1"):
    """Get environment metrics and statistics for the current episode."""
    env = get_env(task_id)
    state = env.state()
    from app.tasks.registry import TASK_REGISTRY
    task = TASK_REGISTRY[task_id]()
    return {
        "task_id":          task_id,
        "episode_active":   env.started,
        "steps_taken":      state.get("step", 0),
        "max_steps":        task.max_steps,
        "steps_remaining":  max(0, task.max_steps - state.get("step", 0)),
        "emails_processed": len(state.get("processed", {})),
        "total_emails":     len(task.get_emails()),
        "coverage_pct":     round(len(state.get("processed", {})) / max(len(task.get_emails()), 1) * 100, 1),
        "cumulative_reward": state.get("cumulative_reward", 0.0),
        "done":             state.get("done", False),
        "pass_threshold":   task.pass_threshold,
        "reward_bounds":    {"min": -1.0, "max": 1.0},
        "dataset_stats": {
            "total_emails":   50,
            "urgent":         12,
            "normal":         15,
            "external":        6,
            "internal":        7,
            "low":             6,
            "spam":            4,
            "critical_emails": 14,
        }
    }

@app.get("/info", tags=["Extended"])
async def get_info():
    """Full environment information — spec, tasks, scoring, dataset summary."""
    from app.tasks.registry import TASK_REGISTRY
    tasks_info = []
    for tid, tcls in TASK_REGISTRY.items():
        t = tcls()
        tasks_info.append({
            "task_id":        tid,
            "name":           t.name,
            "difficulty":     t.difficulty,
            "email_count":    len(t.get_emails()),
            "max_steps":      t.max_steps,
            "pass_threshold": t.pass_threshold,
            "description":    t.description,
        })
    return {
        "name":        "OpenEnv: Email Triage & Response — Peak Edition",
        "version":     "2.0.0",
        "spec":        "openenv-v1",
        "domain":      "enterprise-email-management",
        "dataset": {
            "total_emails": 50,
            "categories":   ["urgent","normal","low","spam","internal","external"],
            "critical_emails": 14,
            "avg_email_length": 75,
        },
        "tasks":        tasks_info,
        "reward": {
            "type":    "shaped",
            "range":   [-1.0, 1.0],
            "signal":  "dense — every step, not just episode end",
            "shaped":  True,
        },
        "endpoints": {
            "core":     ["POST /reset", "POST /step", "GET /state"],
            "grading":  ["POST /grader", "GET /metrics"],
            "extended": ["GET /tasks", "POST /baseline", "GET /leaderboard", "POST /leaderboard/submit", "GET /info"],
            "ui":       ["GET /", "GET /health", "GET /docs"],
        },
        "novelty": [
            "Synonym-aware keyword grading (15 synonym groups per email)",
            "Kendall tau-inspired prioritization scoring",
            "Dense shaped rewards with critical email penalties",
            "Live monitoring dashboard with real-time reward chart",
            "50 curated enterprise emails with full ground truth",
        ]
    }

@app.get("/health", response_class=HTMLResponse)
async def health(fmt: str = "html"):
    from app.data import EMAILS, CATEGORY_COUNTS
    from app.tasks.registry import TASK_REGISTRY
    if fmt == "json":
        from fastapi.responses import JSONResponse
        return JSONResponse({"status": "ok", "version": "2.0.0", "emails": 50, "tasks": 3})

    task_rows = ""
    for tid, tcls in TASK_REGISTRY.items():
        t = tcls()
        dc = {"easy":"#22d75e","medium":"#f97316","hard":"#ef4444"}[t.difficulty]
        task_rows += f"""<tr>
          <td><span style="font-weight:700;color:#fff">{tid}</span></td>
          <td>{t.name}</td>
          <td><span style="color:{dc};font-weight:700">{t.difficulty}</span></td>
          <td>{len(t.get_emails())}</td>
          <td>{t.max_steps}</td>
          <td style="color:#22d75e;font-weight:700">{int(t.pass_threshold*100)}%</td>
        </tr>"""

    cat_bars = ""
    total_emails = len(EMAILS)
    cat_colors = {"urgent":"#ef4444","normal":"#00e5ff","external":"#22d75e","internal":"#a78bfa","low":"#5a6a84","spam":"#eab308"}
    for cat, count in sorted(CATEGORY_COUNTS.items(), key=lambda x: -x[1]):
        pct = round(count / total_emails * 100)
        col = cat_colors.get(cat, "#cdd6e8")
        cat_bars += f"""<div class="cat-row">
          <span class="cat-label" style="color:{col}">{cat}</span>
          <div class="cat-track"><div class="cat-fill" style="width:{pct}%;background:{col}"></div></div>
          <span class="cat-count">{count}</span>
        </div>"""

    endpoints = [
        ("POST", "/reset",    "Reset environment, returns initial observation"),
        ("POST", "/step",     "Execute action → (observation, reward, done, info)"),
        ("GET",  "/state",    "Return full current environment state"),
        ("GET",  "/tasks",    "List all tasks with action schema"),
        ("POST", "/grader",   "Grade current episode — detailed score breakdown"),
        ("POST", "/baseline", "Run baseline agent (requires OPENAI_API_KEY)"),
        ("GET",  "/health",   "This page — system status"),
        ("GET",  "/docs",     "Swagger interactive API documentation"),
    ]
    ep_rows = ""
    for method, path, desc in endpoints:
        mc = "#00e5ff" if method == "POST" else "#22d75e"
        ep_rows += f"""<tr>
          <td><span style="color:{mc};font-weight:700;font-size:10px">{method}</span></td>
          <td><a href="{path}" style="color:#fff;text-decoration:none;font-weight:600">{path}</a></td>
          <td style="color:#5a6a84">{desc}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpenEnv · Health</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@700;800;900&display=swap" rel="stylesheet">
<style>
:root{{--bg:#05080d;--s1:#0a0f18;--s2:#0f1620;--b1:#1a2438;--b2:#243044;--ac:#00e5ff;--g:#22d75e;--t:#cdd6e8;--m:#5a6a84;--mono:'JetBrains Mono',monospace;--sans:'Syne',sans-serif;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--t);font-family:var(--mono);min-height:100vh;}}
body::before{{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(0,229,255,.018) 1px,transparent 1px),linear-gradient(90deg,rgba(0,229,255,.018) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;}}
.topbar{{height:52px;background:var(--s1);border-bottom:1px solid var(--b1);display:flex;align-items:center;padding:0 28px;gap:14px;position:sticky;top:0;z-index:10;}}
.logo{{font-family:var(--sans);font-size:17px;font-weight:900;color:#fff;letter-spacing:-1px;display:flex;align-items:center;gap:9px;text-decoration:none;}}
.logo-box{{width:26px;height:26px;border:2px solid var(--ac);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:13px;color:var(--ac);box-shadow:0 0 10px rgba(0,229,255,.25);}}
.pill{{font-size:10px;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:.5px;text-transform:uppercase;background:rgba(34,215,94,.1);color:var(--g);border:1px solid rgba(34,215,94,.2);}}
.nav-links{{margin-left:auto;display:flex;gap:20px;}}
.nav-links a{{color:var(--m);text-decoration:none;font-size:11px;transition:color .15s;}}
.nav-links a:hover,.nav-links a.active{{color:var(--ac);}}
.page{{max-width:1000px;margin:0 auto;padding:36px 24px;display:flex;flex-direction:column;gap:24px;}}
.page-title{{font-family:var(--sans);font-size:30px;font-weight:900;color:#fff;letter-spacing:-1px;margin-bottom:4px;display:flex;align-items:center;gap:12px;}}
.status-dot{{width:12px;height:12px;border-radius:50%;background:var(--g);box-shadow:0 0 10px var(--g);animation:pulse 2s infinite;flex-shrink:0;}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.grid-4{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}}
.stat-card{{background:var(--s1);border:1px solid var(--b1);border-radius:10px;padding:18px 20px;}}
.stat-label{{font-size:9px;font-weight:700;color:var(--m);text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;}}
.stat-val{{font-family:var(--sans);font-size:30px;font-weight:900;line-height:1;}}
.stat-sub{{font-size:10px;color:var(--m);margin-top:4px;}}
.panel{{background:var(--s1);border:1px solid var(--b1);border-radius:10px;overflow:hidden;}}
.panel-head{{padding:12px 20px;background:var(--s2);border-bottom:1px solid var(--b1);font-size:11px;font-weight:700;color:var(--t);display:flex;justify-content:space-between;align-items:center;}}
.panel-head a{{color:var(--m);font-size:10px;text-decoration:none;}}
.panel-head a:hover{{color:var(--ac);}}
table{{width:100%;border-collapse:collapse;font-size:11px;}}
td,th{{padding:10px 20px;border-bottom:1px solid rgba(255,255,255,.04);text-align:left;}}
th{{font-size:9px;font-weight:700;color:var(--m);text-transform:uppercase;letter-spacing:.8px;background:rgba(255,255,255,.02);}}
tr:last-child td{{border-bottom:none;}}
tr:hover td{{background:rgba(255,255,255,.02);}}
.cat-row{{display:flex;align-items:center;gap:12px;padding:8px 20px;border-bottom:1px solid rgba(255,255,255,.04);}}
.cat-row:last-child{{border-bottom:none;}}
.cat-label{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;min-width:72px;}}
.cat-track{{flex:1;height:6px;background:var(--s2);border-radius:3px;overflow:hidden;}}
.cat-fill{{height:100%;border-radius:3px;}}
.cat-count{{font-size:11px;font-weight:700;color:var(--t);min-width:24px;text-align:right;}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:24px;}}
</style>
</head>
<body>
<div class="topbar">
  <a href="/" class="logo"><div class="logo-box">✉</div>OpenEnv</a>
  <span class="pill">● ONLINE</span>
  <div class="nav-links">
    <a href="/">Dashboard</a>
    <a href="/tasks">Tasks</a>
    <a href="/health" class="active">Health</a>
    <a href="/docs">API Docs</a>
  </div>
</div>
<div class="page">

  <div>
    <div class="page-title"><div class="status-dot"></div>System Health</div>
    <div style="color:var(--m);font-size:12px;margin-top:4px">OpenEnv Email Triage — Peak Edition v2.0.0 · All systems operational</div>
  </div>

  <div class="grid-4">
    <div class="stat-card">
      <div class="stat-label">Status</div>
      <div class="stat-val" style="color:var(--g);font-size:22px">ONLINE</div>
      <div class="stat-sub">All endpoints live</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Version</div>
      <div class="stat-val" style="color:var(--ac);font-size:22px">2.0.0</div>
      <div class="stat-sub">Peak Edition</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Email Dataset</div>
      <div class="stat-val" style="color:#a78bfa">{total_emails}</div>
      <div class="stat-sub">Emails loaded</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Tasks</div>
      <div class="stat-val" style="color:#f97316">3</div>
      <div class="stat-sub">Easy · Medium · Hard</div>
    </div>
  </div>

  <div class="grid-2">
    <div class="panel">
      <div class="panel-head"><span>Tasks</span><a href="/tasks">View all →</a></div>
      <table>
        <tr><th>ID</th><th>Name</th><th>Difficulty</th><th>Emails</th><th>Steps</th><th>Pass</th></tr>
        {task_rows}
      </table>
    </div>
    <div class="panel">
      <div class="panel-head"><span>Dataset — Category Breakdown</span></div>
      {cat_bars}
    </div>
  </div>

  <div class="panel">
    <div class="panel-head"><span>API Endpoints</span><a href="/docs">Swagger UI →</a></div>
    <table>
      <tr><th>Method</th><th>Path</th><th>Description</th></tr>
      {ep_rows}
    </table>
  </div>

</div>
</body></html>"""

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return DASHBOARD_HTML

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))

# ── Dashboard HTML ─────────────────────────────────────────────────────────────
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpenEnv · Email Triage Peak</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,300;0,400;0,600;0,700;1,400&family=Syne:wght@400;700;800;900&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#05080d;--s1:#0a0f18;--s2:#0f1620;--s3:#151e2c;
  --b1:#1a2438;--b2:#243044;
  --ac:#00e5ff;--ac2:#7c3aed;--ac3:#f59e0b;
  --g:#22d75e;--o:#f97316;--r:#ef4444;--y:#eab308;--p:#a78bfa;
  --t:#cdd6e8;--m:#5a6a84;--dim:#2a3a54;
  --mono:'JetBrains Mono',monospace;--sans:'Syne',sans-serif;
}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{height:100%;overflow:hidden;}
body{background:var(--bg);color:var(--t);font-family:var(--mono);font-size:12px;display:flex;flex-direction:column;}

/* scanline overlay */
body::after{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.08) 2px,rgba(0,0,0,0.08) 4px);pointer-events:none;z-index:9999;}

/* grid bg */
body::before{content:'';position:fixed;inset:0;
  background-image:linear-gradient(rgba(0,229,255,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(0,229,255,0.02) 1px,transparent 1px);
  background-size:40px 40px;pointer-events:none;}

/* ── TOP BAR ── */
.topbar{height:48px;background:var(--s1);border-bottom:1px solid var(--b1);display:flex;align-items:center;padding:0 20px;gap:16px;flex-shrink:0;position:relative;z-index:10;}
.logo{font-family:var(--sans);font-size:18px;font-weight:900;color:#fff;letter-spacing:-1px;display:flex;align-items:center;gap:10px;}
.logo-icon{width:26px;height:26px;border:2px solid var(--ac);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:13px;color:var(--ac);box-shadow:0 0 12px rgba(0,229,255,0.3);}
.topbar-pill{font-size:10px;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:.5px;text-transform:uppercase;}
.pill-cyan{background:rgba(0,229,255,.1);color:var(--ac);border:1px solid rgba(0,229,255,.2);}
.pill-green{background:rgba(34,215,94,.1);color:var(--g);border:1px solid rgba(34,215,94,.2);}
.pill-amber{background:rgba(245,158,11,.1);color:var(--ac3);border:1px solid rgba(245,158,11,.2);}
.topbar-right{margin-left:auto;display:flex;align-items:center;gap:20px;}
.live-dot{width:7px;height:7px;border-radius:50%;background:var(--g);box-shadow:0 0 8px var(--g);animation:blink 1.8s infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.topbar-link{color:var(--m);font-size:11px;text-decoration:none;transition:color .15s;}
.topbar-link:hover{color:var(--ac);}

/* ── LAYOUT ── */
.layout{flex:1;display:grid;grid-template-columns:240px 1fr 320px;overflow:hidden;}

/* ── SIDEBAR ── */
.sidebar{background:var(--s1);border-right:1px solid var(--b1);display:flex;flex-direction:column;overflow:hidden;}
.sidebar-section{padding:14px 14px 0;}
.s-label{font-size:9px;font-weight:700;color:var(--m);text-transform:uppercase;letter-spacing:1.2px;margin-bottom:8px;padding-left:2px;}

.task-btn{width:100%;padding:10px 11px;background:transparent;border:1px solid transparent;border-radius:7px;color:var(--t);font-family:var(--mono);font-size:11px;text-align:left;cursor:pointer;margin-bottom:5px;transition:all .15s;position:relative;display:block;}
.task-btn:hover{background:var(--s3);border-color:var(--b2);}
.task-btn.active{background:rgba(0,229,255,.07);border-color:rgba(0,229,255,.25);color:var(--ac);}
.task-btn .tn{font-weight:700;display:block;margin-bottom:2px;}
.task-btn .tm{color:var(--m);font-size:10px;}
.dbadge{position:absolute;right:10px;top:50%;transform:translateY(-50%);font-size:9px;font-weight:700;padding:2px 7px;border-radius:3px;text-transform:uppercase;}
.de{background:rgba(34,215,94,.12);color:var(--g);}
.dm{background:rgba(249,115,22,.12);color:var(--o);}
.dh{background:rgba(239,68,68,.12);color:var(--r);}

.run-btn{width:calc(100%-28px);margin:12px 14px 5px;padding:11px;background:linear-gradient(135deg,rgba(0,229,255,.12),rgba(124,58,237,.12));border:1px solid rgba(0,229,255,.3);border-radius:7px;color:var(--ac);font-family:var(--mono);font-size:11px;font-weight:700;cursor:pointer;letter-spacing:.5px;transition:all .2s;display:block;}
.run-btn:hover{background:linear-gradient(135deg,rgba(0,229,255,.22),rgba(124,58,237,.22));box-shadow:0 0 16px rgba(0,229,255,.15);}
.run-btn:disabled{opacity:.35;cursor:not-allowed;}
.reset-btn{width:calc(100%-28px);margin:0 14px 14px;padding:8px;background:transparent;border:1px solid var(--b1);border-radius:7px;color:var(--m);font-family:var(--mono);font-size:10px;cursor:pointer;transition:all .2s;}
.reset-btn:hover{border-color:var(--o);color:var(--o);}

.ep-list{padding:0 14px 14px;overflow-y:auto;flex:1;}
.ep-item{padding:8px 10px;background:var(--s2);border:1px solid var(--b1);border-radius:6px;margin-bottom:5px;cursor:pointer;transition:all .15s;}
.ep-item:hover{border-color:var(--b2);}
.ep-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;}
.ep-name{font-weight:700;font-size:10px;color:var(--t);}
.ep-score{font-weight:800;font-size:12px;}
.ep-bar-bg{height:3px;background:var(--dim);border-radius:2px;}
.ep-bar-fill{height:100%;border-radius:2px;transition:width .5s;}

/* ── MAIN CENTER ── */
.center{overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;}

/* stat cards */
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;}
.stat{background:var(--s1);border:1px solid var(--b1);border-radius:8px;padding:14px 16px;position:relative;overflow:hidden;}
.stat::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--ac-color,var(--ac));}
.stat-label{font-size:9px;color:var(--m);text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px;}
.stat-val{font-family:var(--sans);font-size:28px;font-weight:900;line-height:1;color:var(--ac-color,var(--ac));}
.stat-sub{font-size:9px;color:var(--m);margin-top:4px;}

/* progress */
.prog-card{background:var(--s1);border:1px solid var(--b1);border-radius:8px;padding:14px 16px;}
.prog-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;}
.prog-title{font-weight:700;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:80%;}
.prog-pct{font-weight:800;font-size:14px;color:var(--ac);flex-shrink:0;}
.prog-track{height:8px;background:var(--s3);border-radius:4px;overflow:hidden;}
.prog-fill{height:100%;background:linear-gradient(90deg,var(--ac),var(--ac2));border-radius:4px;transition:width .5s ease;box-shadow:0 0 10px rgba(0,229,255,.35);}

/* reward chart */
.reward-chart-wrap{background:var(--s1);border:1px solid var(--b1);border-radius:8px;padding:14px 16px;}
.chart-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;}
.chart-title{font-weight:700;font-size:11px;}
#reward-canvas{width:100%;height:70px;display:block;}

/* email feed */
.feed-card{background:var(--s1);border:1px solid var(--b1);border-radius:8px;overflow:hidden;flex:1;}
.card-head{padding:10px 14px;background:var(--s2);border-bottom:1px solid var(--b1);display:flex;align-items:center;justify-content:space-between;}
.card-title{font-weight:700;font-size:11px;display:flex;align-items:center;gap:8px;}
.c-count{font-size:9px;color:var(--m);background:var(--b1);padding:2px 8px;border-radius:10px;}
.feed-body{overflow-y:auto;max-height:300px;}
.feed-row{display:grid;grid-template-columns:48px 1fr 76px 68px 80px;gap:10px;align-items:center;padding:9px 14px;border-bottom:1px solid rgba(255,255,255,.03);transition:background .1s;font-size:11px;}
.feed-row:hover{background:var(--s2);}
.feed-row.done{opacity:.45;}
.feed-id{font-weight:700;color:var(--m);font-size:10px;}
.feed-subj{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--t);}
.feed-from{font-size:10px;color:var(--m);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.tag{font-size:9px;font-weight:700;padding:2px 7px;border-radius:3px;text-transform:uppercase;white-space:nowrap;text-align:center;}
.tag-urgent{background:rgba(239,68,68,.15);color:var(--r);}
.tag-normal{background:rgba(0,229,255,.1);color:var(--ac);}
.tag-low{background:rgba(90,106,132,.15);color:var(--m);}
.tag-spam{background:rgba(234,179,8,.1);color:var(--y);}
.tag-internal{background:rgba(167,139,250,.12);color:var(--p);}
.tag-external{background:rgba(34,215,94,.1);color:var(--g);}
.tag-pending{background:transparent;color:transparent;border:1px solid var(--dim);}
.act-escalate{background:rgba(239,68,68,.12);color:var(--r);}
.act-respond{background:rgba(34,215,94,.12);color:var(--g);}
.act-archive{background:rgba(90,106,132,.1);color:var(--m);}
.act-triage{background:rgba(0,229,255,.1);color:var(--ac);}
.act-flag{background:rgba(234,179,8,.1);color:var(--y);}
.act-pending{background:transparent;color:transparent;}
.rwd-pos{color:var(--g);font-weight:700;text-align:right;}
.rwd-neg{color:var(--r);font-weight:700;text-align:right;}
.rwd-neu{color:var(--m);text-align:right;}

/* ── RIGHT PANEL ── */
.right{background:var(--s1);border-left:1px solid var(--b1);display:flex;flex-direction:column;overflow:hidden;}
.rp-head{padding:12px 16px;border-bottom:1px solid var(--b1);background:var(--s2);font-weight:700;font-size:11px;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;}
.rp-tabs{display:flex;gap:1px;background:var(--b1);border-radius:6px;padding:2px;margin:12px 16px 0;flex-shrink:0;}
.rp-tab{flex:1;padding:6px;text-align:center;font-size:10px;font-weight:700;color:var(--m);cursor:pointer;border-radius:5px;transition:all .15s;}
.rp-tab.active{background:var(--s3);color:var(--ac);}

/* score ring */
.score-section{padding:16px;display:flex;align-items:center;gap:16px;border-bottom:1px solid var(--b1);flex-shrink:0;}
.ring-wrap{position:relative;width:88px;height:88px;flex-shrink:0;}
.ring-svg{transform:rotate(-90deg);}
.ring-track{fill:none;stroke:var(--s3);}
.ring-fill{fill:none;stroke-linecap:round;transition:stroke-dashoffset .9s ease;}
.ring-center{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;}
.ring-num{font-family:var(--sans);font-size:24px;font-weight:900;line-height:1;}
.ring-lbl{font-size:9px;color:var(--m);text-transform:uppercase;}
.score-info{flex:1;}
.score-status{font-family:var(--sans);font-size:17px;font-weight:800;margin-bottom:4px;}
.score-sub{font-size:10px;color:var(--m);line-height:1.6;}

/* breakdown */
.breakdown-wrap{padding:12px 16px;overflow-y:auto;flex:1;}
.bd-row{margin-bottom:10px;}
.bd-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;}
.bd-key{font-size:10px;color:var(--m);}
.bd-val{font-size:11px;font-weight:800;}
.bd-track{height:5px;background:var(--s3);border-radius:3px;overflow:hidden;}
.bd-fill{height:100%;border-radius:3px;transition:width .7s ease;}

/* log */
.log-section{display:flex;flex-direction:column;flex:1;overflow:hidden;}
.log-inner{overflow-y:auto;padding:8px 14px;flex:1;}
.log-line{display:flex;gap:10px;padding:4px 0;border-bottom:1px solid rgba(255,255,255,.025);font-size:10.5px;line-height:1.5;}
.log-t{color:var(--m);min-width:70px;flex-shrink:0;font-size:9.5px;}
.lo{color:var(--g)}.lw{color:var(--o)}.le{color:var(--r)}.li{color:var(--ac)}.ld{color:var(--m)}
.log-bar{font-family:var(--mono);font-size:10px;letter-spacing:-1px;}
.log-clear{background:none;border:none;color:var(--m);cursor:pointer;font-size:10px;font-family:var(--mono);padding:0;}
.log-clear:hover{color:var(--r);}

/* scrollbars */
::-webkit-scrollbar{width:3px;height:3px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:var(--b1);border-radius:2px;}

@keyframes slideUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.slide-up{animation:slideUp .2s ease forwards;}
</style>
</head>
<body>

<div class="topbar">
  <div class="logo">
    <div class="logo-icon">✉</div>
    OpenEnv
  </div>
  <span class="topbar-pill pill-cyan">EMAIL TRIAGE</span>
  <span class="topbar-pill pill-amber">PEAK EDITION</span>
  <span class="topbar-pill pill-green">50 EMAILS</span>
  <div class="topbar-right">
    <div class="live-dot"></div>
    <span style="font-size:10px;color:var(--m)">LIVE</span>
    <a href="/docs" class="topbar-link">API DOCS →</a>
    <a href="/redoc" class="topbar-link">REDOC →</a>
  </div>
</div>

<div class="layout">

<!-- ── SIDEBAR ── -->
<aside class="sidebar">
  <div class="sidebar-section">
    <div class="s-label">Select Task</div>
    <button class="task-btn active" onclick="selectTask('task_1',this)">
      <span class="tn">Email Triage</span>
      <span class="tm">20 emails · 25 steps</span>
      <span class="dbadge de">Easy</span>
    </button>
    <button class="task-btn" onclick="selectTask('task_2',this)">
      <span class="tn">Response Drafting</span>
      <span class="tm">15 emails · 25 steps</span>
      <span class="dbadge dm">Medium</span>
    </button>
    <button class="task-btn" onclick="selectTask('task_3',this)">
      <span class="tn">Inbox Zero Sprint</span>
      <span class="tm">50 emails · 55 steps</span>
      <span class="dbadge dh">Hard</span>
    </button>
  </div>

  <button class="run-btn" id="run-btn" onclick="runDemo()">▶ RUN DEMO EPISODE</button>
  <button class="reset-btn" onclick="resetEnv()">↺ RESET ENVIRONMENT</button>

  <div class="sidebar-section">
    <div class="s-label">Past Episodes</div>
  </div>
  <div class="ep-list" id="ep-list">
    <div style="font-size:10px;color:var(--m);text-align:center;padding:12px 0">No episodes yet</div>
  </div>

  <div style="padding:10px 14px;border-top:1px solid var(--b1);margin-top:auto;">
    <div class="s-label" style="margin-bottom:6px">Endpoints</div>
    <div style="font-size:10px;line-height:2.2;color:var(--m);">
      <span style="color:var(--ac)">POST</span> /reset &nbsp; <span style="color:var(--ac)">POST</span> /step<br>
      <span style="color:var(--g)">GET</span> /state &nbsp;&nbsp; <span style="color:var(--g)">GET</span> /tasks<br>
      <span style="color:var(--ac)">POST</span> /grader &nbsp; <span style="color:var(--ac)">POST</span> /baseline
    </div>
  </div>
</aside>

<!-- ── CENTER ── -->
<main class="center">

  <div class="stats-row">
    <div class="stat" style="--ac-color:var(--ac)">
      <div class="stat-label">Current Step</div>
      <div class="stat-val" id="s-step">—</div>
      <div class="stat-sub" id="s-maxstep">of — max</div>
    </div>
    <div class="stat" style="--ac-color:var(--g)">
      <div class="stat-label">Processed</div>
      <div class="stat-val" id="s-proc">—</div>
      <div class="stat-sub" id="s-total">of — emails</div>
    </div>
    <div class="stat" style="--ac-color:var(--ac3)">
      <div class="stat-label">Cumul. Reward</div>
      <div class="stat-val" id="s-reward">—</div>
      <div class="stat-sub">shaped ±1.0/step</div>
    </div>
    <div class="stat" style="--ac-color:var(--p)">
      <div class="stat-label">Progress</div>
      <div class="stat-val" id="s-prog">—</div>
      <div class="stat-sub">task completion</div>
    </div>
  </div>

  <div class="prog-card">
    <div class="prog-head">
      <span class="prog-title" id="prog-desc">Select a task and click Run Demo Episode</span>
      <span class="prog-pct" id="prog-pct">0%</span>
    </div>
    <div class="prog-track"><div class="prog-fill" id="prog-fill" style="width:0%"></div></div>
  </div>

  <div class="reward-chart-wrap">
    <div class="chart-header">
      <span class="chart-title">⚡ Reward Per Step</span>
      <span style="font-size:10px;color:var(--m)" id="chart-info">—</span>
    </div>
    <canvas id="reward-canvas" height="70"></canvas>
  </div>

  <div class="feed-card">
    <div class="card-head">
      <span class="card-title">📧 Inbox Feed <span class="c-count" id="feed-count">—</span></span>
      <span style="font-size:10px;color:var(--m)" id="feed-status">Awaiting reset…</span>
    </div>
    <div class="feed-body" id="feed-body">
      <div style="padding:24px;text-align:center;color:var(--m)">Click "Run Demo Episode" to start</div>
    </div>
  </div>

</main>

<!-- ── RIGHT PANEL ── -->
<aside class="right">
  <div class="rp-head">
    <span>Episode Score</span>
    <span style="font-size:10px;color:var(--m)" id="rp-task">—</span>
  </div>

  <div class="score-section" id="score-section">
    <div style="padding:20px;text-align:center;color:var(--m);font-size:11px;width:100%">
      Score appears after episode
    </div>
  </div>

  <div class="rp-tabs">
    <div class="rp-tab active" onclick="showTab('breakdown',this)">Breakdown</div>
    <div class="rp-tab" onclick="showTab('log',this)">Live Log</div>
  </div>

  <div id="tab-breakdown" class="breakdown-wrap">
    <div style="text-align:center;color:var(--m);font-size:11px;padding:20px 0">Run an episode to see breakdown</div>
  </div>

  <div id="tab-log" class="log-section" style="display:none">
    <div class="rp-head" style="flex-shrink:0;border-top:1px solid var(--b1);">
      <span>Live Log</span>
      <button class="log-clear" onclick="clearLog()">CLEAR</button>
    </div>
    <div class="log-inner" id="log"></div>
  </div>
</aside>

</div>

<script>
const BASE=''; let task='task_1'; let emailData=[]; let stepResults={}; let rewardHistory=[]; let episodes=[];

// ── Reward chart ─────────────────────────────────────────────────────────────
const canvas=document.getElementById('reward-canvas');
const ctx=canvas.getContext('2d');
function drawChart(){
  const W=canvas.offsetWidth, H=70;
  canvas.width=W; canvas.height=H;
  ctx.clearRect(0,0,W,H);
  if(rewardHistory.length<2){
    ctx.fillStyle='rgba(90,106,132,0.3)';
    ctx.fillRect(0,H/2-0.5,W,1);
    return;
  }
  const n=rewardHistory.length;
  const step=W/Math.max(n-1,1);
  // zero line
  ctx.strokeStyle='rgba(90,106,132,0.3)'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(0,H/2); ctx.lineTo(W,H/2); ctx.stroke();
  // area fill
  const grad=ctx.createLinearGradient(0,0,0,H);
  grad.addColorStop(0,'rgba(0,229,255,0.2)'); grad.addColorStop(1,'rgba(0,229,255,0.0)');
  ctx.beginPath(); ctx.moveTo(0,H/2);
  rewardHistory.forEach((v,i)=>{ const x=i*step; const y=H/2 - v*(H/2-4); i===0?ctx.moveTo(x,y):ctx.lineTo(x,y); });
  ctx.lineTo((n-1)*step,H/2); ctx.lineTo(0,H/2); ctx.closePath();
  ctx.fillStyle=grad; ctx.fill();
  // line
  ctx.beginPath(); ctx.strokeStyle='var(--ac)'; ctx.lineWidth=1.5; ctx.lineJoin='round';
  rewardHistory.forEach((v,i)=>{ const x=i*step; const y=H/2-v*(H/2-4); i===0?ctx.moveTo(x,y):ctx.lineTo(x,y); });
  ctx.stroke();
  // dots for last point
  const lx=(n-1)*step; const ly=H/2-rewardHistory[n-1]*(H/2-4);
  ctx.beginPath(); ctx.arc(lx,ly,3,0,Math.PI*2);
  ctx.fillStyle=rewardHistory[n-1]>=0?'var(--g)':'var(--r)'; ctx.fill();
  document.getElementById('chart-info').textContent=`${n} steps | last: ${rewardHistory[n-1]>=0?'+':''}${rewardHistory[n-1].toFixed(3)}`;
}
window.addEventListener('resize',drawChart);

// ── Tabs ────────────────────────────────────────────────────────────────────
function showTab(t,btn){
  document.getElementById('tab-breakdown').style.display=t==='breakdown'?'':'none';
  document.getElementById('tab-log').style.display=t==='log'?'flex':'none';
  document.querySelectorAll('.rp-tab').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
}

// ── Log ──────────────────────────────────────────────────────────────────────
function log(msg,type='i'){
  const el=document.getElementById('log');
  const t=new Date().toTimeString().slice(0,8);
  const cls=type==='o'?'lo':type==='w'?'lw':type==='e'?'le':type==='d'?'ld':'li';
  const d=document.createElement('div');
  d.className='log-line slide-up';
  d.innerHTML=`<span class="log-t">${t}</span><span class="${cls}">${msg}</span>`;
  el.prepend(d); if(el.children.length>200)el.removeChild(el.lastChild);
}
function clearLog(){document.getElementById('log').innerHTML='';}

// ── Stats ────────────────────────────────────────────────────────────────────
function updateStats(obs){
  const step=obs.step??'—'; const ms=obs.context?.max_steps??'—';
  const proc=obs.processed_count??'—'; const tot=obs.inbox?.length??'—';
  const rew=obs.cumulative_reward??0; const prog=obs.progress??0;
  document.getElementById('s-step').textContent=step;
  document.getElementById('s-maxstep').textContent=`of ${ms} max`;
  document.getElementById('s-proc').textContent=proc;
  document.getElementById('s-total').textContent=`of ${tot} emails`;
  const re=document.getElementById('s-reward');
  re.textContent=typeof rew==='number'?rew.toFixed(3):rew;
  re.style.color=rew>0?'var(--g)':rew<0?'var(--r)':'var(--ac3)';
  document.getElementById('s-prog').textContent=Math.round(prog*100)+'%';
  document.getElementById('prog-pct').textContent=Math.round(prog*100)+'%';
  document.getElementById('prog-fill').style.width=Math.round(prog*100)+'%';
  document.getElementById('feed-count').textContent=`${proc}/${tot}`;
}

// ── Feed ────────────────────────────────────────────────────────────────────
function renderFeed(){
  const el=document.getElementById('feed-body'); el.innerHTML='';
  emailData.forEach(e=>{
    const r=stepResults[e.id]; const done=!!r;
    const cat=r?.category||'pending'; const act=r?.action_type||'pending'; const rew=r?.reward;
    const rStr=rew==null?'—':(rew>0?'+':'')+rew.toFixed(3);
    const rCls=rew==null?'rwd-neu':rew>0?'rwd-pos':'rwd-neg';
    const row=document.createElement('div');
    row.className=`feed-row${done?' done':''} slide-up`;
    row.innerHTML=`<span class="feed-id">${e.id}</span>
      <div><div class="feed-subj">${e.subject}</div><div class="feed-from">${e.sender}</div></div>
      <span class="tag tag-${cat}">${cat==='pending'?'—':cat}</span>
      <span class="tag act-${act}">${act==='pending'?'—':act}</span>
      <span class="${rCls}">${rStr}</span>`;
    el.appendChild(row);
  });
}

// ── Score ───────────────────────────────────────────────────────────────────
const KEY_LABELS={avg_category_accuracy:'Category Accuracy',avg_priority_accuracy:'Priority Accuracy',avg_action_accuracy:'Action Accuracy',avg_action_correctness:'Action Correctness',avg_keyword_coverage:'Keyword Coverage',avg_completeness:'Completeness',avg_tone:'Tone Quality',coverage:'Email Coverage',quality_score:'Quality Score',prioritization:'Prioritization',critical_handling:'Critical Emails',step_efficiency:'Step Efficiency'};
const SKIP=new Set(['final_score','critical_missed']);
function renderScore(grade){
  const sc=grade.episode_score??0; const passed=grade.passed;
  const color=sc>=0.85?'var(--g)':sc>=0.70?'var(--ac)':sc>=0.55?'var(--o)':'var(--r)';
  const r=38,cx=44,cy=44,circ=2*Math.PI*r;
  document.getElementById('score-section').innerHTML=`
    <div class="ring-wrap">
      <svg width="88" height="88" class="ring-svg">
        <circle class="ring-track" cx="${cx}" cy="${cy}" r="${r}" stroke-width="7"/>
        <circle class="ring-fill" cx="${cx}" cy="${cy}" r="${r}" stroke-width="7" stroke="${color}"
          stroke-dasharray="${circ}" stroke-dashoffset="${circ*(1-sc)}"/>
      </svg>
      <div class="ring-center">
        <span class="ring-num" style="color:${color}">${Math.round(sc*100)}</span>
        <span class="ring-lbl">/ 100</span>
      </div>
    </div>
    <div class="score-info">
      <div class="score-status" style="color:${passed?'var(--g)':'var(--r)'}">${passed?'✓ PASSED':'✗ FAILED'}</div>
      <div class="score-sub">Threshold: ${Math.round((grade.pass_threshold??0.75)*100)}%<br>
        ${grade.emails_processed??'?'}/${grade.total_emails??'?'} emails · ${grade.steps_taken??'?'} steps</div>
    </div>`;
  document.getElementById('rp-task').textContent=grade.task_id;
  const bd=grade.breakdown??{};
  const rows=Object.keys(bd).filter(k=>!SKIP.has(k)&&k!=='quality_score').map(k=>{
    const v=bd[k]; if(typeof v!=='number')return'';
    const pct=Math.min(100,Math.round(v*100));
    const bc=pct>=85?'var(--g)':pct>=70?'var(--ac)':pct>=55?'var(--o)':'var(--r)';
    const lbl=KEY_LABELS[k]||k.split('_').map(w=>w[0].toUpperCase()+w.slice(1)).join(' ');
    return `<div class="bd-row"><div class="bd-head"><span class="bd-key">${lbl}</span>
      <span class="bd-val" style="color:${bc}">${pct}%</span></div>
      <div class="bd-track"><div class="bd-fill" style="width:${pct}%;background:${bc}"></div></div></div>`;
  }).join('');
  document.getElementById('tab-breakdown').innerHTML=rows||'<div style="color:var(--m);font-size:11px;padding:16px;text-align:center">No breakdown data</div>';
  // Save episode
  episodes.unshift({task,score:sc,passed,time:new Date().toTimeString().slice(0,5)});
  renderEpisodes();
}

function renderEpisodes(){
  const el=document.getElementById('ep-list');
  if(!episodes.length){el.innerHTML='<div style="font-size:10px;color:var(--m);text-align:center;padding:12px 0">No episodes yet</div>';return;}
  el.innerHTML=episodes.slice(0,8).map((ep,i)=>{
    const pct=Math.round(ep.score*100);
    const c=ep.passed?'var(--g)':pct>=60?'var(--o)':'var(--r)';
    return `<div class="ep-item"><div class="ep-top"><span class="ep-name">${ep.task} · ${ep.time}</span>
      <span class="ep-score" style="color:${c}">${pct}</span></div>
      <div class="ep-bar-bg"><div class="ep-bar-fill" style="width:${pct}%;background:${c}"></div></div></div>`;
  }).join('');
}

// ── Task select ──────────────────────────────────────────────────────────────
function selectTask(tid,btn){
  task=tid; stepResults={}; rewardHistory=[]; drawChart();
  document.querySelectorAll('.task-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  log(`Selected task: ${tid}`,'i');
  resetEnv();
}

async function resetEnv(){
  try{
    const r=await fetch(`${BASE}/reset?task_id=${task}`,{method:'POST'});
    const d=await r.json(); const obs=d.observation;
    emailData=obs.inbox||[]; stepResults={}; rewardHistory=[];
    updateStats(obs); renderFeed(); drawChart();
    document.getElementById('prog-desc').textContent=(obs.task_description||'').slice(0,70)+'…';
    document.getElementById('feed-status').textContent=`${emailData.length} emails loaded`;
    log(`Reset OK — ${emailData.length} emails, max ${obs.context?.max_steps} steps`,'o');
  }catch(e){log(`Reset failed: ${e.message}`,'e');}
}

// ── Demo actions ─────────────────────────────────────────────────────────────
const DEMO={
  task_1:[
    {action_type:'escalate',email_id:'e001',category:'urgent',priority_score:1.0,escalate_to:'backend-oncall',reason:'P0 production database down, 45k users impacted'},
    {action_type:'escalate',email_id:'e003',category:'urgent',priority_score:0.99,escalate_to:'security-team',reason:'Tor exit node login with 2FA bypass'},
    {action_type:'respond', email_id:'e004',category:'urgent',priority_score:1.0,response_text:'I hereby authorize proceeding with all GDPR breach notifications, mandatory password resets for affected accounts, and full legal compliance coordination. Please proceed immediately.'},
    {action_type:'respond', email_id:'e002',category:'urgent',priority_score:0.97,response_text:'Hi Sarah, I have the Q4 budget data ready. Sending headcount projections with Q3 variances, revised capex schedule, and team lead sign-off now. You will have everything before 9:45 AM.'},
    {action_type:'escalate',email_id:'e006',category:'urgent',priority_score:0.98,escalate_to:'engineering-lead',reason:'Payment gateway down, $47K/hour revenue loss, need emergency authorization'},
    {action_type:'escalate',email_id:'e008',category:'urgent',priority_score:0.95,escalate_to:'cloud-ops',reason:'AWS Lambda runaway, $84K unexpected billing in 24h'},
    {action_type:'respond', email_id:'e041',category:'urgent',priority_score:0.96,response_text:'SSL certificate expiry is critical. Escalating to DevOps for immediate manual renewal. Ticket #DEV-8821 is being actioned now.',escalate_to:'devops'},
    {action_type:'respond', email_id:'e007',category:'urgent',priority_score:0.94,response_text:'HIPAA audit findings received. I will prepare a response plan addressing all 3 HIGH severity findings within the 48-hour deadline. Remediation for PHI encryption and BAA gaps will begin immediately.'},
    {action_type:'respond', email_id:'e005',category:'urgent',priority_score:0.92,response_text:'I confirm rejection of clause 9.1 (unlimited liability for data breach) and clause 11.3 (IP ownership of derivative works). Please proceed with counter-offer removing those clauses. The Net-15 payment terms in 4.2 are acceptable.'},
    {action_type:'respond', email_id:'e047',category:'urgent',priority_score:0.93,response_text:'Hi, updating the board deck now. ARR on slide 14 corrected to $8.48M including the Stripe expansion. NRR on slide 22 corrected to 118%. Updated deck coming by 8 AM. Thanks for catching this.'},
    {action_type:'respond', email_id:'e042',category:'urgent',priority_score:0.88,response_text:'Thank you for flagging this. I will address the team directly today with a clear all-hands statement clarifying our position on the rumors. Please help me draft the message and schedule 30 minutes this afternoon.'},
    {action_type:'respond', email_id:'e012',category:'normal',priority_score:0.88,response_text:'Dear Jennifer, I apologize for the billing discrepancy on invoice INV-2024-891. Investigating the seat count difference, missing enterprise discount per contract ENT-2021-004, and incorrect billing period. Will resolve and issue corrected invoice within 24 hours.'},
    {action_type:'respond', email_id:'e016',category:'normal',priority_score:0.85,response_text:'I approve the 15% discount and SLA upgrade to 99.99% for the Acme Corp 3-year renewal worth $240K ARR. Please also allocate a dedicated CSM. This deal must close by Jan 22. Proceed with the final contract.'},
    {action_type:'respond', email_id:'e020',category:'normal',priority_score:0.80,response_text:'I approve the $15K emergency customer success budget. The NPS drop from 67 to 34 is critical. Priority actions: fix support response time to meet SLA, and fast-track bulk export and SSO features.'},
    {action_type:'respond', email_id:'e044',category:'normal',priority_score:0.91,response_text:'Approving the custom rate limit exception for Salesforce at 5K requests per minute to retain the $420K ARR enterprise account. Please document this as a custom enterprise tier and update the contract accordingly.'},
    {action_type:'respond', email_id:'e017',category:'normal',priority_score:0.78,response_text:'Approved. Counter Maya Patel at $205K base salary, maintaining the current equity package. This is a strong candidate and worth retaining. Please send the counter offer before Thursday 5 PM.'},
    {action_type:'respond', email_id:'e009',category:'normal',priority_score:0.72,response_text:'Approved full refund of $147.99 for premium customer Jane Rodriguez, order ORD-88234. As a 3-year premium customer this must be processed immediately with a personal apology note. Please confirm completion.'},
    {action_type:'respond', email_id:'e019',category:'normal',priority_score:0.68,response_text:'Recommending option B for the Cloudflare contract — renegotiate to approximately $25K given the 30% usage drop. Please initiate negotiations before January 18 to allow sufficient time before auto-renewal.'},
    {action_type:'archive', email_id:'e021',category:'internal',priority_score:0.35},
    {action_type:'archive', email_id:'e022',category:'internal',priority_score:0.28},
  ],
  task_2:[
    {action_type:'respond',email_id:'e002',priority_score:0.97,response_text:"Hi Sarah, I apologize for the delay. Sending Q4 budget now: headcount projections with variances, revised capex schedule, and team lead sign-off. All numbers attached and ready — you will have everything before board this morning at 9:30. Best regards."},
    {action_type:'escalate',email_id:'e003',priority_score:0.99,escalate_to:'security-team',response_text:"Escalating to the security team and SOC immediately. Suspicious Tor login with 2FA bypass detected — unauthorized access risk. Locking account and investigating now. Please review and report findings urgently. Security team notified."},
    {action_type:'respond',email_id:'e004',priority_score:1.0,response_text:"I hereby authorize proceeding immediately: GDPR-compliant breach notification letters to all 12,000 affected customers within 72 hours, mandatory password reset for all affected accounts now, full compliance coordination. Urgent — proceed without delay. Authorized."},
    {action_type:'respond',email_id:'e005',priority_score:0.92,response_text:"Reject clause 9.1 (unlimited liability for data breach — not acceptable) and clause 11.3 (IP ownership of derivative works — not acceptable). Proceed with counter-offer removing those clauses from the Acme contract. Negotiate final terms today before the deadline."},
    {action_type:'escalate',email_id:'e006',priority_score:0.98,escalate_to:'engineering-lead',response_text:"Authorizing emergency escalation to engineering lead and on-call devops team immediately. Payment gateway and Stripe are down — this is critical and urgent. $47K revenue loss per hour. Approve vendor escalation now. Engineering ops must act immediately."},
    {action_type:'respond',email_id:'e007',priority_score:0.94,response_text:"HIPAA response plan to Deloitte audit within 48-hour deadline: remediation for PHI encryption at rest, fix access log retention compliance, execute BAA with all missing cloud vendors. Plan will address all findings urgently. Will respond by the deadline."},
    {action_type:'escalate',email_id:'e008',priority_score:0.95,escalate_to:'cloud-ops',response_text:"Escalating to cloud-ops and devops — urgent. AWS Lambda runaway billing $84,000 unexpected charge. Investigate the invocation loop, remediate and disable the runaway function in production immediately. This is an emergency — critical prod account issue."},
    {action_type:'respond',email_id:'e009',priority_score:0.72,response_text:"Dear Support, approved: issue full refund and credit to Jane Rodriguez, valued premium customer, for order ORD-88234. Apologize sincerely for the inconvenience. Please process this immediately and confirm with the customer. Thank you."},
    {action_type:'respond',email_id:'e010',priority_score:0.52,response_text:"Hi Alex, I reviewed the DataSync integration proposal and the revenue share co-marketing model. Would like to schedule a follow-up call with the partnership team this week to discuss. Please share your availability. Best regards."},
    {action_type:'respond',email_id:'e011',priority_score:0.62,response_text:"Alex Thompson onboarding confirmed — checklist complete: laptop provisioned, Slack and GitHub access granted, 1:1 scheduled Monday at 10 AM. Everything is done and confirmed. Will be ready by Friday EOD."},
    {action_type:'respond',email_id:'e012',priority_score:0.88,response_text:"Apologize for the billing discrepancy on invoice INV-2024-891. Investigating the seat count difference, missing enterprise discount, and billing period issue. Will resolve, credit, and correct the invoice within 24 hours as a priority. Resolving now asap."},
    {action_type:'respond',email_id:'e013',priority_score:0.47,response_text:"Reviewed the Figma v2.0 mockup designs — the navigation restructure, mobile-first responsive approach, and color palette all look great. Will provide detailed written feedback and comments by Wednesday EOD. Thanks for sharing."},
    {action_type:'respond',email_id:'e014',priority_score:0.58,response_text:"Thank you and congratulations! I am truly honored, excited, and grateful for the promotion to Senior Director. Look forward to taking on the expanded responsibilities and discussing the announcement with my manager. Effective February — thank you so much."},
    {action_type:'respond',email_id:'e015',priority_score:0.43,response_text:"Will submit Q1 OKRs with objectives and key results by Friday January 19 EOD deadline. Goals aligned to Q1 growth, retention, and team priorities. Submitting before the deadline."},
    {action_type:'respond',email_id:'e016',priority_score:0.85,response_text:"Approved — 15% discount accepted, 99.99% SLA uptime guaranteed, dedicated CSM customer success manager allocated. Proceed with the Acme Corp renewal deal by Jan 22. Terms approved."},
  ],
  task_3:[
      {action_type:'escalate',email_id:'e001',category:'urgent',priority_score:1.0,escalate_to:'backend-oncall'},
      {action_type:'respond',email_id:'e004',category:'urgent',priority_score:1.0,response_text:"I hereby authorize all GDPR breach notifications to 12000 affected customers within 72-hour deadline, mandatory password resets immediately. Proceed now."},
      {action_type:'escalate',email_id:'e003',category:'urgent',priority_score:0.99,escalate_to:'security-team'},
      {action_type:'escalate',email_id:'e006',category:'urgent',priority_score:0.98,escalate_to:'engineering-lead'},
      {action_type:'respond',email_id:'e002',category:'urgent',priority_score:0.97,response_text:"Hi Sarah, sending Q4 budget now: headcount projections with variances, capex schedule, sign-off. Will have everything before 9:45 AM."},
      {action_type:'escalate',email_id:'e041',category:'urgent',priority_score:0.96,escalate_to:'devops'},
      {action_type:'escalate',email_id:'e008',category:'urgent',priority_score:0.95,escalate_to:'cloud-ops'},
      {action_type:'respond',email_id:'e007',category:'urgent',priority_score:0.94,response_text:"HIPAA response plan within 48 hours: PHI encryption fix, access log retention, BAA vendor compliance. Deloitte findings addressed."},
      {action_type:'respond',email_id:'e047',category:'urgent',priority_score:0.93,response_text:"Updating board deck: ARR slide 14 corrected to 8.48M, NRR slide 22 to 118%. Will have ready by 8 AM before print deadline."},
      {action_type:'respond',email_id:'e005',category:'urgent',priority_score:0.92,response_text:"Reject clause 9.1 unlimited liability and clause 11.3 IP derivative works from Acme contract. Proceed with counter-offer today."},
      {action_type:'respond',email_id:'e044',category:'normal',priority_score:0.91,response_text:"Approving custom rate limit exception 5K requests per minute for Salesforce to retain $420K ARR account."},
      {action_type:'respond',email_id:'e039',category:'external',priority_score:0.89,response_text:"Approving Stripe expansion: 99.99% SLA, dedicated CSM, SAML SSO. $280K ARR contract by Jan 31."},
      {action_type:'respond',email_id:'e012',category:'normal',priority_score:0.88,response_text:"Apologize for billing discrepancy INV-2024-891. Investigating seats, discount, billing period. Will resolve within 24 hours."},
      {action_type:'respond',email_id:'e042',category:'urgent',priority_score:0.88,response_text:"Scheduling all-hands statement today to clarify company position on layoff rumors. Draft transparent message for team this afternoon."},
      {action_type:'respond',email_id:'e043',category:'urgent',priority_score:0.87,response_text:"Authorizing legal team response. Our position: $17K payable for delivered work, $28K disputed per SOW section 3.2."},
      {action_type:'respond',email_id:'e016',category:'normal',priority_score:0.85,response_text:"Approving 15% discount, 99.99% SLA, dedicated CSM for Acme Corp $240K ARR renewal. Close by Jan 22."},
      {action_type:'respond',email_id:'e020',category:'normal',priority_score:0.8,response_text:"Approving $15K emergency CS budget. Priority: fix support response time and fast-track bulk export and SSO features."},
      {action_type:'respond',email_id:'e017',category:'normal',priority_score:0.78,response_text:"Counter Maya Patel at $205K base, maintaining equity package. Send offer before Thursday 5 PM."},
      {action_type:'respond',email_id:'e048',category:'normal',priority_score:0.77,response_text:"Acknowledging ISO 27001 pre-audit. Will sign off on security policy, risk register, vendor assessments by Jan 25."},
      {action_type:'respond',email_id:'e037',category:'external',priority_score:0.75,response_text:"Confirming Gartner Magic Quadrant participation. Arranging 2-hour briefing and 3 customer references by Jan 22."},
      {action_type:'respond',email_id:'e045',category:'normal',priority_score:0.73,response_text:"Approving 2-week tech debt sprint Feb 5-16. Security vulnerabilities and payment reliability must be addressed."},
      {action_type:'respond',email_id:'e009',category:'normal',priority_score:0.72,response_text:"Approving full refund $147.99 for premium customer Jane Rodriguez order ORD-88234. Process immediately with apology."},
      {action_type:'respond',email_id:'e036',category:'external',priority_score:0.71,response_text:"Confirming Zapier featured partner status by Jan 19. Approving co-branded landing page and press release."},
      {action_type:'respond',email_id:'e049',category:'normal',priority_score:0.7,response_text:"Go ahead and schedule preliminary call with Meshify. At $45-65M range this acquisition is worth exploring."},
      {action_type:'respond',email_id:'e019',category:'normal',priority_score:0.68,response_text:"Recommending renegotiation of Cloudflare contract to $25K given 30% usage drop. Initiate before Jan 18."},
      {action_type:'respond',email_id:'e038',category:'external',priority_score:0.68,response_text:"Confirming Forbes interview for CEO before Jan 24. Will send scheduling availability today."},
      {action_type:'respond',email_id:'e018',category:'normal',priority_score:0.66,response_text:"Confirmed: AI-001 Redis alert is now unblocked. AI-002 circuit breaker and AI-003 runbook updates on track."},
      {action_type:'respond',email_id:'e046',category:'normal',priority_score:0.65,response_text:"Approved: reallocate $200K from events to paid acquisition: $150K paid search, $50K content. Launch Feb 1."},
      {action_type:'respond',email_id:'e011',category:'normal',priority_score:0.62,response_text:"Alex Thompson onboarding confirmed: laptop provisioned, Slack GitHub access granted, 1:1 scheduled Monday 10 AM. Will confirm Friday."},
      {action_type:'respond',email_id:'e040',category:'external',priority_score:0.6,response_text:"Confirming CTO for AWS re:Invent keynote on AI infrastructure at scale. Will confirm topic by Feb 1."},
      {action_type:'respond',email_id:'e014',category:'internal',priority_score:0.58,response_text:"Thank you for the wonderful promotion news! Truly thrilled and honored. Excited for expanded responsibilities. Looking forward to February."},
      {action_type:'respond',email_id:'e050',category:'normal',priority_score:0.55,response_text:"Approving $85K engineering offsite budget for March 18-20 in Napa. Book venue by Jan 22."},
      {action_type:'respond',email_id:'e010',category:'external',priority_score:0.52,response_text:"Hi Alex, reviewed DataSync proposal and revenue share model. Would like to schedule a follow-up call this week. Best regards."},
      {action_type:'respond',email_id:'e013',category:'normal',priority_score:0.47,response_text:"Reviewed Figma v2.0 mockups. Navigation restructure, mobile-first, color palette great. Will provide detailed feedback by Wednesday EOD."},
      {action_type:'respond',email_id:'e015',category:'internal',priority_score:0.43,response_text:"Will submit Q1 OKRs with objectives and key results aligned to growth and platform priorities by Friday Jan 19 EOD."},
      {action_type:'archive',email_id:'e021',category:'internal',priority_score:0.35},
      {action_type:'archive',email_id:'e023',category:'internal',priority_score:0.32},
      {action_type:'archive',email_id:'e022',category:'internal',priority_score:0.28},
      {action_type:'archive',email_id:'e029',category:'internal',priority_score:0.22},
      {action_type:'archive',email_id:'e024',category:'low',priority_score:0.18},
      {action_type:'archive',email_id:'e025',category:'internal',priority_score:0.15},
      {action_type:'archive',email_id:'e035',category:'low',priority_score:0.09},
      {action_type:'archive',email_id:'e028',category:'low',priority_score:0.08},
      {action_type:'archive',email_id:'e026',category:'low',priority_score:0.05},
      {action_type:'archive',email_id:'e034',category:'low',priority_score:0.04},
      {action_type:'archive',email_id:'e027',category:'low',priority_score:0.02},
      {action_type:'archive',email_id:'e030',category:'spam',priority_score:0.0},
      {action_type:'archive',email_id:'e031',category:'spam',priority_score:0.0},
      {action_type:'archive',email_id:'e032',category:'spam',priority_score:0.0},
      {action_type:'archive',email_id:'e033',category:'spam',priority_score:0.0},
  ]
};

// ── Run demo ─────────────────────────────────────────────────────────────────
async function runDemo(){
  const btn=document.getElementById('run-btn');
  btn.disabled=true; btn.textContent='⏳ RUNNING…';
  stepResults={}; rewardHistory=[];
  showTab('log',document.querySelectorAll('.rp-tab')[1]);
  try{
    log(`▶ Starting demo — ${task}`,'i');
    const r0=await fetch(`${BASE}/reset?task_id=${task}`,{method:'POST'});
    const d0=await r0.json(); emailData=d0.observation.inbox||[];
    updateStats(d0.observation); renderFeed(); drawChart();
    document.getElementById('prog-desc').textContent=(d0.observation.task_description||'').slice(0,70)+'…';
    const actions=DEMO[task]||[];
    let lastObs=d0.observation; let totalR=0;
    for(let i=0;i<actions.length;i++){
      const a=actions[i];
      await new Promise(r=>setTimeout(r,task==='task_3'?120:220));
      const sr=await fetch(`${BASE}/step?task_id=${task}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(a)});
      if(!sr.ok){log(`Step error ${sr.status}`,'e');continue;}
      const sd=await sr.json();
      lastObs=sd.observation; const rew=sd.reward; totalR+=rew;
      stepResults[a.email_id]={...a,reward:rew};
      rewardHistory.push(rew); if(rewardHistory.length>60)rewardHistory.shift();
      updateStats(sd.observation); renderFeed(); drawChart();
      const rStr=(rew>=0?'+':'')+rew.toFixed(3);
      const cat=a.category?` cat:${a.category}`:a.escalate_to?` → ${a.escalate_to}`:'';
      const pri=a.priority_score!=null?` pri:${a.priority_score.toFixed(2)}`:'';
      const tp=rew>0.1?'o':rew<-0.05?'w':'i';
      log(`[${a.email_id}] ${a.action_type.toUpperCase().padEnd(8)} ${rStr}${cat}${pri}  (${i+1}/${actions.length})`,tp);
      if(sd.done){log('Episode complete (done=true)','o');break;}
    }
    await new Promise(r=>setTimeout(r,350));
    log('Fetching grade…','i');
    const gr=await fetch(`${BASE}/grader?task_id=${task}`,{method:'POST'});
    const grade=await gr.json();
    renderScore(grade);
    showTab('breakdown',document.querySelectorAll('.rp-tab')[0]);
    log(`Score: ${grade.episode_score.toFixed(4)} — ${grade.passed?'PASSED ✓':'FAILED ✗'}`,grade.passed?'o':'w');
    const bd=grade.breakdown||{}; const skip=new Set(['final_score','critical_missed']);
    Object.entries(bd).forEach(([k,v])=>{
      if(skip.has(k)||typeof v!=='number')return;
      const pct=Math.min(100,Math.round(v*100));
      const bar='█'.repeat(Math.round(pct/10))+'░'.repeat(10-Math.round(pct/10));
      const lbl=(KEY_LABELS[k]||k).padEnd(22);
      log(`  ${lbl} ${bar} ${pct}%`,pct>=80?'o':pct>=60?'w':'e');
    });
  }catch(e){log(`Error: ${e.message}`,'e');}
  finally{btn.disabled=false;btn.textContent='▶ RUN DEMO EPISODE';}
}

window.onload=()=>{
  log('OpenEnv Peak Edition v2.0 initialized','o');
  log('50 emails · 3 tasks · full graders','i');
  resetEnv();
};
</script>
</body>
</html>"""
