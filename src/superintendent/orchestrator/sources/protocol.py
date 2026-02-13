"""TaskSource abstract base class definition."""

from abc import ABC, abstractmethod

from superintendent.orchestrator.sources.models import Task, TaskStatus


class TaskSource(ABC):
    """Base class for task source backends.

    All task sources must subclass this. The orchestrator is agnostic
    about where tasks come from — it only cares about getting tasks
    and updating their status.
    """

    @abstractmethod
    def get_tasks(self) -> list[Task]: ...

    @abstractmethod
    def get_ready_tasks(self) -> list[Task]: ...

    @abstractmethod
    def update_status(self, task_id: str, status: TaskStatus) -> None: ...

    @abstractmethod
    def claim_task(self, task_id: str, agent_id: str) -> bool: ...
