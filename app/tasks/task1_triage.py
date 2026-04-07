from __future__ import annotations
from app.data import EMAIL_BY_ID, TASK_1_EMAILS

MAX_CAT = 0.40; MAX_PRI = 0.30; MAX_ACT = 0.30

class TriageTask:
    task_id = "task_1"; name = "Email Triage"; difficulty = "easy"
    description = ("Process 20 emails: assign correct category (urgent/normal/low/spam/internal/external), "
                   "priority score (0–1), and take the right action (triage/archive/escalate/respond/flag). "
                   "Goal: Perfect categorization, accurate priorities, correct actions.")
    max_steps = 25; pass_threshold = 0.75

    def __init__(self):
        self.emails = [EMAIL_BY_ID[i] for i in TASK_1_EMAILS]

    def get_emails(self): return self.emails

    def grade_action(self, action: dict, email: dict) -> dict:
        gt = email["ground_truth"]; c = {}
        pc = action.get("category"); tc = gt["category"]
        c["category_correct"] = 0.40 if pc == tc else (0.20 if pc in _related(tc) else 0.0)
        pp = action.get("priority_score")
        if pp is not None:
            err = abs(float(pp) - gt["priority_score"])
            c["priority_accuracy"] = 0.30 if err<=0.10 else 0.25 if err<=0.25 else 0.15 if err<=0.40 else 0.05 if err<=0.60 else 0.0
        else:
            c["priority_accuracy"] = 0.0
        ca = gt["correct_action"]; ta = action.get("action_type")
        c["action_correct"] = 0.30 if ta==ca else (0.20 if _acceptable(ta,ca) else 0.0)
        return {"total": round(sum(c.values()), 4), "components": c}

    def compute_episode_score(self, graded: list[dict]) -> dict:
        if not graded: return {"score": 0.0, "breakdown": {}}
        n = len(graded); tot = len(self.emails)
        q = sum(g["total"] for g in graded) / n
        cov = n / tot
        score = q * (0.80 + 0.20 * cov)
        bd = {
            "avg_category_accuracy": round(sum(g["components"].get("category_correct",0) for g in graded)/n / MAX_CAT, 4),
            "avg_priority_accuracy": round(sum(g["components"].get("priority_accuracy",0) for g in graded)/n / MAX_PRI, 4),
            "avg_action_accuracy":   round(sum(g["components"].get("action_correct",0)   for g in graded)/n / MAX_ACT, 4),
            "coverage":              round(cov, 4),
            "quality_score":         round(q, 4),
            "final_score":           round(score, 4),
        }
        return {"score": round(score, 4), "breakdown": bd}


def _related(cat):
    return {"urgent":["normal","external"],"normal":["urgent","low","internal","external"],
            "low":["normal","internal"],"spam":["low"],"internal":["normal","low"],
            "external":["normal","urgent"]}.get(cat,[])

def _acceptable(taken, correct):
    ok = {"archive":{"skip","archive","triage"},"respond":{"respond","compose","triage"},
          "escalate":{"escalate","flag","respond"},"flag":{"flag","escalate"},
          "triage":{"triage","archive","flag"}}
    return taken in ok.get(correct, set())
