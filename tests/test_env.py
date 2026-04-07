"""Full OpenEnv spec compliance + grader tests."""
import sys; sys.path.insert(0,'.')
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health"); assert r.status_code==200
    assert r.json()["status"]=="ok"

def test_tasks_returns_3():
    r = client.get("/tasks"); d = r.json()
    assert d["count"]==3
    diffs = {t["difficulty"] for t in d["tasks"]}
    assert diffs == {"easy","medium","hard"}

def test_tasks_have_action_schema():
    for t in client.get("/tasks").json()["tasks"]:
        s = t["action_schema"]
        assert "properties" in s and "action_type" in s["properties"]

@pytest.mark.parametrize("tid", ["task_1","task_2","task_3"])
def test_reset_returns_observation(tid):
    r = client.post(f"/reset?task_id={tid}")
    assert r.status_code==200
    obs = r.json()["observation"]
    for f in ["step","inbox","task_description","task_id","progress","cumulative_reward","available_actions"]:
        assert f in obs, f"Missing {f}"
    assert obs["step"]==0
    assert obs["progress"]==0.0

def test_task1_has_20_emails():
    obs = client.post("/reset?task_id=task_1").json()["observation"]
    assert len(obs["inbox"])==20

def test_task2_has_15_emails():
    obs = client.post("/reset?task_id=task_2").json()["observation"]
    assert len(obs["inbox"])==15

def test_task3_has_50_emails():
    obs = client.post("/reset?task_id=task_3").json()["observation"]
    assert len(obs["inbox"])==50

def test_step_returns_required_fields():
    client.post("/reset?task_id=task_1")
    r = client.post("/step?task_id=task_1", json={"action_type":"archive","email_id":"e021"})
    assert r.status_code==200
    for f in ["observation","reward","done","info"]: assert f in r.json()

def test_reward_bounds_all_tasks():
    for tid,eid in [("task_1","e021"),("task_2","e010"),("task_3","e030")]:
        client.post(f"/reset?task_id={tid}")
        r = client.post(f"/step?task_id={tid}", json={"action_type":"archive","email_id":eid})
        reward = r.json()["reward"]
        assert -1.0<=reward<=1.0, f"{tid} reward {reward} out of bounds"

def test_correct_action_positive_reward():
    client.post("/reset?task_id=task_1")
    r = client.post("/step?task_id=task_1", json={"action_type":"escalate","email_id":"e001","category":"urgent","priority_score":1.0,"escalate_to":"backend-oncall"})
    assert r.json()["reward"] > 0

def test_archive_critical_penalized():
    client.post("/reset?task_id=task_3")
    r = client.post("/step?task_id=task_3", json={"action_type":"archive","email_id":"e001"})
    assert r.json()["reward"] < 0

def test_duplicate_action_penalized():
    client.post("/reset?task_id=task_1")
    a = {"action_type":"archive","email_id":"e022"}
    client.post("/step?task_id=task_1", json=a)
    r2 = client.post("/step?task_id=task_1", json=a)
    assert r2.json()["reward"] < 0

def test_state_endpoint():
    client.post("/reset?task_id=task_1")
    r = client.get("/state?task_id=task_1")
    assert r.status_code==200
    s = r.json()["state"]
    assert "step" in s and "task_id" in s and "processed" in s

def test_full_episode_grade_task1():
    client.post("/reset?task_id=task_1")
    from app.data import EMAIL_BY_ID, TASK_1_EMAILS
    for eid in TASK_1_EMAILS:
        e=EMAIL_BY_ID[eid]; gt=e["ground_truth"]
        client.post("/step?task_id=task_1", json={"action_type":gt["correct_action"],"email_id":eid,"category":gt["category"],"priority_score":gt["priority_score"]})
    g = client.post("/grader?task_id=task_1").json()
    assert 0.0<=g["episode_score"]<=1.0
    assert g["episode_score"]>=0.90, f"Perfect T1 should be >=0.90, got {g['episode_score']}"
    assert g["passed"]==True
    bd = g["breakdown"]
    for k in ["avg_category_accuracy","avg_priority_accuracy","avg_action_accuracy"]:
        assert bd[k]>=0.85, f"{k}={bd[k]} should be >=0.85"

def test_grader_breakdown_normalized():
    """All breakdown values must be 0.0–1.0 (shown as %)."""
    client.post("/reset?task_id=task_1")
    from app.data import TASK_1_EMAILS, EMAIL_BY_ID
    for eid in TASK_1_EMAILS[:5]:
        client.post("/step?task_id=task_1",json={"action_type":"archive","email_id":eid,"priority_score":0.5})
    bd = client.post("/grader?task_id=task_1").json()["breakdown"]
    for k,v in bd.items():
        if isinstance(v,float): assert 0.0<=v<=1.0, f"{k}={v} not in [0,1]"

def test_invalid_email_id_handled():
    client.post("/reset?task_id=task_1")
    r = client.post("/step?task_id=task_1",json={"action_type":"archive","email_id":"e999"})
    assert r.status_code==200
    assert r.json()["reward"]<0
