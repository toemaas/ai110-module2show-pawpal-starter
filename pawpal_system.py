from dataclasses import dataclass, field


@dataclass
class Task:
    id: str
    title: str
    duration_minutes: int
    priority: str = "medium"
    category: str = "general"
    recurrence: str = "none"
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def is_high_priority(self) -> bool:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def edit_task(self, task_id: str, **changes) -> None:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int = 0
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_daily_plan(self) -> list[Task]:
        pass

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    def fits_in_time(self, task: Task, minutes_left: int) -> bool:
        pass

    def detect_conflicts(self, plan: list[Task]) -> list[Task]:
        pass

    def explain_plan(self, plan: list[Task]) -> str:
        pass
