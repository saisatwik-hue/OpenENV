from __future__ import annotations
import copy, time
from typing import Any
from app.models import Action, Observation, EmailSnapshot
from app.data import EMAIL_BY_ID
from app.tasks.registry import TASK_REGISTRY


class EmailTriageEnv:
    def __init__(self, task_id="task_1"):
        self.task_id = task_id
        self.task = TASK_REGISTRY[task_id]()
        self._reset_state()
        self.started = False

    def _reset_state(self):
        self._step = 0
        self._reward_total = 0.0
        self._processed: dict[str, dict] = {}
        self._graded: list[dict] = []
        self._order: list[tuple] = []
        self._done = False

    def reset(self) -> Observation:
        self.task = TASK_REGISTRY[self.task_id]()
        self._reset_state()
        self.started = True
        emails = self.task.get_emails()
        inbox = [_snap(e) for e in emails]
        self._state = {
            "step": 0, "task_id": self.task_id,
            "emails": {e["id"]: _snap(e).model_dump() for e in emails},
            "processed": {}, "pending_ids": [e["id"] for e in emails],
            "cumulative_reward": 0.0, "done": False,
        }
        return self._obs(emails, inbox)

    def step(self, action: Action):
        if not self.started or self._done:
            raise ValueError("Call reset() first")
        self._step += 1
        emails = self.task.get_emails()
        emap = {e["id"]: e for e in emails}
        eid = action.email_id

        if eid not in emap:
            r = -0.05
            self._reward_total += r
            return self._obs(emails, [_snap(e) for e in emails]), r, False, {"error": f"Unknown email {eid}"}

        if eid in self._processed:
            r = -0.10
            self._reward_total += r
            return self._obs(emails, [_snap(e) for e in emails]), r, self._check_done(), {"warning": "Already processed"}

        email = emap[eid]
        ad = action.model_dump()
        graded = self._grade(ad, email)
        r = _shape(graded, email)
        if self._step > self.task.max_steps: r -= 0.05

        self._processed[eid] = ad
        self._order.append((eid, action.action_type))
        self._graded.append(graded)
        self._reward_total += r
        self._state["processed"][eid] = ad
        if eid in self._state["pending_ids"]: self._state["pending_ids"].remove(eid)
        self._state["step"] = self._step
        self._state["cumulative_reward"] = round(self._reward_total, 4)
        done = self._check_done()
        self._done = done
        self._state["done"] = done
        obs = self._obs(emails, [_snap(e) for e in emails])
        return obs, round(r, 4), done, {
            "email_id": eid, "action_type": action.action_type,
            "step_reward": round(r, 4), "graded": graded,
            "step": self._step, "processed_count": len(self._processed),
        }

    def state(self) -> dict: return copy.deepcopy(self._state)

    def grade(self) -> dict:
        if self.task_id == "task_3":
            res = self.task.compute_episode_score(self._graded, self._step, self._order)
        else:
            res = self.task.compute_episode_score(self._graded)
        # Clamp strictly between 0 and 1 exclusive — validator rejects 0.0 and 1.0 exactly
        sc = max(0.0001, min(0.9999, res["score"]))
        passed = sc >= self.task.pass_threshold
        grade_letter = "A" if sc>=0.90 else "B" if sc>=0.80 else "C" if sc>=0.70 else "D" if sc>=0.60 else "F"
        return {
            "task_id": self.task_id, "episode_score": round(sc, 4),
            "breakdown": res["breakdown"],
            "summary": f"{'✅ PASSED' if passed else '❌ FAILED'} | Grade: {grade_letter} | Score: {sc:.3f} | Processed: {len(self._processed)}/{len(self.task.get_emails())} | Task: {self.task_id}",
            "pass_threshold": self.task.pass_threshold, "passed": passed,
            "steps_taken": self._step, "emails_processed": len(self._processed),
            "total_emails": len(self.task.get_emails()),
        }

    def _grade(self, ad, email):
        if self.task_id == "task_1": return self.task.grade_action(ad, email)
        if self.task_id == "task_2": return self.task.grade_response(ad, email)
        return self.task.grade_action(ad, email)

    def _check_done(self):
        return len(self._processed) >= len(self.task.get_emails()) or self._step >= self.task.max_steps

    def _obs(self, emails, inbox):
        pid = set(self._processed.keys())
        pending = [e["id"] for e in emails if e["id"] not in pid]
        cur = EMAIL_BY_ID.get(pending[0]) if pending else None
        return Observation(
            step=self._step, inbox=inbox,
            processed_count=len(pid), pending_count=len(pending),
            current_email=_snap(cur) if cur else None,
            current_email_body=cur["body"] if cur else None,
            task_description=self.task.description, task_id=self.task_id,
            progress=round(len(pid)/max(len(emails),1), 4),
            cumulative_reward=round(self._reward_total, 4),
            available_actions=["triage","respond","escalate","archive","flag","skip"],
            context={"max_steps": self.task.max_steps, "total_emails": len(emails), "pending_ids": pending[:5]},
        )


def _snap(e):
    return EmailSnapshot(
        id=e["id"], subject=e["subject"], sender=e["sender"],
        sender_domain=e["sender_domain"], timestamp=e["timestamp"],
        preview=e["body"][:200], has_attachments=e.get("has_attachments",False),
        thread_depth=e.get("thread_depth",0), word_count=e.get("word_count",0),
    )

def _shape(graded, email):
    base = graded.get("total", 0.0)
    r = (base - 0.5) * 0.8
    if base >= 0.85: r += 0.1
    if email["ground_truth"]["priority_score"] >= 0.9 and base <= 0.1: r -= 0.2
    return round(max(-1.0, min(1.0, r)), 4)
