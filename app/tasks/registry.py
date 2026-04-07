from app.tasks.task1_triage import TriageTask
from app.tasks.task2_response import ResponseTask
from app.tasks.task3_inbox_zero import InboxZeroTask

TASK_REGISTRY = {
    "task_1": TriageTask,
    "task_2": ResponseTask,
    "task_3": InboxZeroTask,
}
