from dataclasses import dataclass, field, fields
from datetime import datetime, time, timedelta
from typing import Optional

PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}


def _minutes(t: time) -> int:
    return t.hour * 60 + t.minute


@dataclass
class Task:
    id: str
    title: str
    duration_minutes: int
    priority: str = "medium"
    category: str = "general"
    recurrence: str = "none"
    completed: bool = False
    pet_name: str = ""
    start_time: Optional[time] = None

    @property
    def end_time(self) -> Optional[time]:
        """Return start_time plus duration, or None if the task is unscheduled."""
        if self.start_time is None:
            return None
        start = datetime.combine(datetime.today(), self.start_time)
        return (start + timedelta(minutes=self.duration_minutes)).time()

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is 'high'."""
        return self.priority.lower() == "high"


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet, rejecting duplicate task ids."""
        if any(t.id == task.id for t in self.tasks):
            raise ValueError(f"Task id '{task.id}' already exists for {self.name}")
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given id, raising KeyError if not found."""
        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                del self.tasks[i]
                return
        raise KeyError(f"No task '{task_id}' for {self.name}")

    def edit_task(self, task_id: str, **changes) -> None:
        """Update fields on a task by id, validating the field names first."""
        valid = {f.name for f in fields(Task)} - {"id", "pet_name"}
        bad = set(changes) - valid
        if bad:
            raise ValueError(f"Cannot edit field(s): {', '.join(sorted(bad))}")
        for t in self.tasks:
            if t.id == task_id:
                for key, value in changes.items():
                    setattr(t, key, value)
                return
        raise KeyError(f"No task '{task_id}' for {self.name}")


@dataclass
class Owner:
    name: str
    available_minutes: int = 0
    day_start: time = time(8, 0)
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's household."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every pet's tasks combined into one list."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.skipped: list[Task] = []

    def generate_daily_plan(self) -> list[Task]:
        """Build a greedy daily plan across all pets within the owner's time budget."""
        pending = [t for t in self.owner.get_all_tasks() if not t.completed]
        minutes_left = self.owner.available_minutes
        clock = datetime.combine(datetime.today(), self.owner.day_start)
        plan: list[Task] = []
        self.skipped = []

        for task in self.sort_tasks(pending):
            if self.fits_in_time(task, minutes_left):
                task.start_time = clock.time()
                clock += timedelta(minutes=task.duration_minutes)
                minutes_left -= task.duration_minutes
                plan.append(task)
            else:
                task.start_time = None
                self.skipped.append(task)
        return plan

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (high first), then shortest duration first."""
        return sorted(
            tasks,
            key=lambda t: (-PRIORITY_RANK.get(t.priority.lower(), 0), t.duration_minutes),
        )

    def fits_in_time(self, task: Task, minutes_left: int) -> bool:
        """Return True if the task's duration fits in the remaining minutes."""
        return task.duration_minutes <= minutes_left

    def detect_conflicts(self, plan: list[Task]) -> list[Task]:
        """Return tasks whose time slot overlaps another task in the plan."""
        timed = [t for t in plan if t.start_time is not None]
        conflicts: list[Task] = []
        for i, a in enumerate(timed):
            a_start = _minutes(a.start_time)
            a_end = a_start + a.duration_minutes
            for b in timed[i + 1:]:
                b_start = _minutes(b.start_time)
                b_end = b_start + b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    for t in (a, b):
                        if t not in conflicts:
                            conflicts.append(t)
        return conflicts

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a readable schedule with the ordering rule and any skipped tasks."""
        if not plan:
            return "No tasks scheduled."
        lines = [f"Daily plan for {self.owner.name} "
                 f"({self.owner.available_minutes} min available):"]
        for t in plan:
            start = t.start_time.strftime("%H:%M") if t.start_time else "--:--"
            who = f" [{t.pet_name}]" if t.pet_name else ""
            lines.append(f"  {start} - {t.title}{who} ({t.duration_minutes} min) "
                         f"[priority: {t.priority}]")
        used = sum(t.duration_minutes for t in plan)
        lines.append(f"Ordered by priority (high first), then shortest first. "
                     f"Used {used} of {self.owner.available_minutes} min.")
        if self.skipped:
            names = ", ".join(f"{t.title} ({t.pet_name})" for t in self.skipped)
            lines.append(f"Skipped (not enough time left): {names}")
        return "\n".join(lines)
