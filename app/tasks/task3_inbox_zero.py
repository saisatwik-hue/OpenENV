from __future__ import annotations
from app.data import EMAIL_BY_ID, TASK_3_EMAILS


class InboxZeroTask:
    task_id = "task_3"; name = "Inbox Zero Sprint"; difficulty = "hard"
    description = ("50 emails. 50 steps. Process everything: triage, respond, escalate, archive. "
                   "Critical emails (priority ≥ 0.88) must be handled first — missing them costs heavily. "
                   "Prioritization order matters: urgent before normal before low before spam. "
                   "Goal: 100% coverage, perfect prioritization, zero missed emergencies.")
    max_steps = 55; pass_threshold = 0.68

    def __init__(self):
        self.emails = [EMAIL_BY_ID[i] for i in TASK_3_EMAILS]
        self._critical = {e["id"] for e in self.emails if e["ground_truth"]["priority_score"]>=0.88}

    def get_emails(self): return self.emails

    def grade_action(self, action: dict, email: dict) -> dict:
        from app.tasks.task1_triage import TriageTask, _acceptable
        from app.tasks.task2_response import ResponseTask
        gt = email["ground_truth"]; at = action.get("action_type","skip"); c = {}
        if at in ("triage",):
            g = TriageTask().grade_action(action, email); base = g["total"]
        elif at in ("respond","compose"):
            base = ResponseTask().grade_response(action,email)["total"] if gt.get("requires_response") else 0.15
        elif at == "escalate":
            base = (0.95 if action.get("escalate_to") else 0.75) if gt["correct_action"]=="escalate" else 0.10
        elif at in ("archive","skip"):
            base = 0.80 if gt["category"]=="spam" else (0.65 if not gt.get("requires_response") and gt["category"] not in ("urgent",) else 0.0)
        elif at == "flag":
            base = 0.60 if gt["correct_action"] in ("escalate","flag") else 0.10
        else: base = 0.0
        c["base"] = base
        if email["id"] in self._critical:
            if at in ("respond","escalate","flag") and base>0.3: c["critical_bonus"]=0.10
            elif at in ("archive","skip"):                       c["critical_penalty"]=-0.25
        return {"total": max(0.0,round(sum(c.values()),4)), "components": c}

    def compute_episode_score(self, graded, step_count, order):
        n=len(self.emails); nc=len(self._critical)
        if not graded: return {"score":0.0,"breakdown":{}}
        ng=len(graded)
        quality   = sum(max(0,g["total"]) for g in graded)/n
        coverage  = ng/n
        priority  = _prioritization(order, self.emails)
        crit_ok   = sum(1 for eid,at in order if eid in self._critical and at in ("respond","escalate","flag"))
        crit_score= crit_ok/max(nc,1)
        efficiency= max(0.0, 1.0-(step_count/self.max_steps)*0.25)
        final = 0.30*quality + 0.25*coverage + 0.20*priority + 0.15*crit_score + 0.10*efficiency
        missed = nc - crit_ok
        if missed>0: final = max(0.0, final - 0.04*missed)
        bd = {"quality_score":round(quality,4),"coverage":round(coverage,4),
              "prioritization":round(priority,4),"critical_handling":round(crit_score,4),
              "step_efficiency":round(efficiency,4),"critical_missed":missed,"final_score":round(final,4)}
        return {"score":round(final,4),"breakdown":bd}


def _prioritization(order, emails):
    if len(order)<2: return 0.7
    pri={e["id"]:e["ground_truth"]["priority_score"] for e in emails}
    ids=[eid for eid,_ in order]
    c=d=0
    for i in range(len(ids)):
        for j in range(i+1,len(ids)):
            if pri.get(ids[i],0)>=pri.get(ids[j],0): c+=1
            else: d+=1
    return round(c/(c+d),4) if c+d else 0.5
