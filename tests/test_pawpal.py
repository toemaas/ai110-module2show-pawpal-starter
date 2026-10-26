from datetime import date, time

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def make_scheduler(*pets):
    owner = Owner(name="Sam", available_minutes=240)
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner)


def test_mark_complete_changes_task_status():
    task = Task(id="t1", title="Morning walk", duration_minutes=30)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task(id="t1", title="Morning walk", duration_minutes=30))
    assert len(pet.tasks) == 1

    pet.add_task(Task(id="t2", title="Feeding", duration_minutes=10))
    assert len(pet.tasks) == 2


# --- Sorting correctness -----------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    tasks = [
        Task(id="c", title="Evening", duration_minutes=10, start_time=time(18, 0)),
        Task(id="a", title="Morning", duration_minutes=10, start_time=time(7, 30)),
        Task(id="b", title="Noon", duration_minutes=10, start_time=time(12, 0)),
    ]

    result = make_scheduler().sort_by_time(tasks)

    assert [t.id for t in result] == ["a", "b", "c"]


def test_sort_by_time_puts_unscheduled_tasks_last():
    tasks = [
        Task(id="none", title="Unscheduled", duration_minutes=10),
        Task(id="late", title="Late", duration_minutes=10, start_time=time(20, 0)),
        Task(id="midnight", title="Midnight", duration_minutes=10, start_time=time(0, 0)),
    ]

    result = make_scheduler().sort_by_time(tasks)

    assert [t.id for t in result] == ["midnight", "late", "none"]


def test_sort_by_time_handles_empty_list_and_does_not_mutate_input():
    scheduler = make_scheduler()
    assert scheduler.sort_by_time([]) == []

    tasks = [
        Task(id="b", title="B", duration_minutes=5, start_time=time(9, 0)),
        Task(id="a", title="A", duration_minutes=5, start_time=time(8, 0)),
    ]
    scheduler.sort_by_time(tasks)
    assert [t.id for t in tasks] == ["b", "a"]


def test_sort_by_time_is_stable_for_equal_start_times():
    tasks = [
        Task(id="first", title="First", duration_minutes=5, start_time=time(9, 0)),
        Task(id="second", title="Second", duration_minutes=5, start_time=time(9, 0)),
    ]

    result = make_scheduler().sort_by_time(tasks)

    assert [t.id for t in result] == ["first", "second"]


def test_generated_plan_is_in_chronological_order():
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(Task(id="low", title="Brush", duration_minutes=10, priority="low"))
    pet.add_task(Task(id="high", title="Meds", duration_minutes=5, priority="high"))
    pet.add_task(Task(id="med", title="Walk", duration_minutes=30))
    scheduler = make_scheduler(pet)

    plan = scheduler.generate_daily_plan()

    assert [t.id for t in plan] == ["high", "med", "low"]
    assert plan == scheduler.sort_by_time(plan)


# --- Recurrence logic --------------------------------------------------------

def test_completing_daily_task_creates_task_for_next_day():
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(Task(id="walk", title="Walk", duration_minutes=30,
                      recurrence="daily", due_date=date(2026, 10, 26)))
    scheduler = make_scheduler(pet)

    following = scheduler.complete_task("Biscuit", "walk")

    assert following is not None
    assert following.due_date == date(2026, 10, 27)
    assert following.completed is False
    assert following.title == "Walk"
    assert following.pet_name == "Biscuit"
    assert following in pet.tasks
    assert len(pet.tasks) == 2
    assert pet.tasks[0].completed is True


def test_completing_weekly_task_creates_task_seven_days_later():
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(Task(id="bath", title="Bath", duration_minutes=20,
                      recurrence="weekly", due_date=date(2026, 12, 28)))

    following = make_scheduler(pet).complete_task("Biscuit", "bath")

    assert following.due_date == date(2027, 1, 4)  # crosses the year boundary


def test_daily_recurrence_handles_leap_day():
    task = Task(id="walk", title="Walk", duration_minutes=30,
                recurrence="daily", due_date=date(2028, 2, 28))

    assert task.next_occurrence().due_date == date(2028, 2, 29)


def test_non_recurring_task_creates_no_follow_up():
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(Task(id="vet", title="Vet", duration_minutes=60, recurrence="none"))

    following = make_scheduler(pet).complete_task("Biscuit", "vet")

    assert following is None
    assert len(pet.tasks) == 1


def test_completing_same_task_twice_does_not_duplicate_occurrence():
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(Task(id="walk", title="Walk", duration_minutes=30,
                      recurrence="daily", due_date=date(2026, 10, 26)))
    scheduler = make_scheduler(pet)

    scheduler.complete_task("Biscuit", "walk")
    second = scheduler.complete_task("Biscuit", "walk")

    assert second is None
    assert len(pet.tasks) == 2


def test_recurrence_id_does_not_chain_suffixes():
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(Task(id="walk", title="Walk", duration_minutes=30,
                      recurrence="daily", due_date=date(2026, 10, 26)))
    scheduler = make_scheduler(pet)

    day2 = scheduler.complete_task("Biscuit", "walk")
    day3 = scheduler.complete_task("Biscuit", day2.id)

    assert day2.id == "walk@2026-10-27"
    assert day3.id == "walk@2026-10-28"


def test_next_occurrence_resets_start_time_and_keeps_other_fields():
    task = Task(id="meds", title="Meds", duration_minutes=5, priority="high",
                recurrence="Daily", start_time=time(8, 0), due_date=date(2026, 10, 26))

    following = task.next_occurrence()

    assert following is not task
    assert following.start_time is None
    assert following.priority == "high"
    assert following.duration_minutes == 5


def test_unknown_recurrence_value_returns_none():
    task = Task(id="x", title="X", duration_minutes=5, recurrence="monthly")

    assert task.next_occurrence() is None


def test_complete_task_raises_for_unknown_pet_or_task():
    pet = Pet(name="Biscuit", species="dog")
    scheduler = make_scheduler(pet)

    with pytest.raises(KeyError):
        scheduler.complete_task("Ghost", "walk")
    with pytest.raises(KeyError):
        scheduler.complete_task("Biscuit", "missing")


# --- Conflict detection ------------------------------------------------------

def test_conflict_warnings_flag_duplicate_start_times():
    dog = Pet(name="Biscuit", species="dog")
    cat = Pet(name="Mochi", species="cat")
    dog.add_task(Task(id="walk", title="Walk", duration_minutes=30, start_time=time(9, 0)))
    cat.add_task(Task(id="feed", title="Feed", duration_minutes=15, start_time=time(9, 0)))
    scheduler = make_scheduler(dog, cat)

    warnings = scheduler.conflict_warnings()

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Feed" in warnings[0]
    assert "different pets" in warnings[0]


def test_conflict_warning_labels_same_pet_overlap():
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(Task(id="a", title="Walk", duration_minutes=30, start_time=time(9, 0)))
    pet.add_task(Task(id="b", title="Bath", duration_minutes=30, start_time=time(9, 15)))

    warnings = make_scheduler(pet).conflict_warnings()

    assert len(warnings) == 1
    assert "same pet" in warnings[0]


def test_detect_conflicts_returns_both_tasks_with_same_start_time():
    a = Task(id="a", title="A", duration_minutes=30, start_time=time(9, 0))
    b = Task(id="b", title="B", duration_minutes=30, start_time=time(9, 0))
    c = Task(id="c", title="C", duration_minutes=30, start_time=time(11, 0))

    conflicts = make_scheduler().detect_conflicts([a, b, c])

    assert conflicts == [a, b]


def test_back_to_back_tasks_are_not_conflicts():
    a = Task(id="a", title="A", duration_minutes=30, start_time=time(9, 0))
    b = Task(id="b", title="B", duration_minutes=30, start_time=time(9, 30))
    scheduler = make_scheduler()

    assert scheduler.detect_conflicts([a, b]) == []
    assert scheduler.conflict_warnings([a, b]) == []


def test_fully_contained_task_is_a_conflict():
    outer = Task(id="o", title="Outer", duration_minutes=120, start_time=time(9, 0))
    inner = Task(id="i", title="Inner", duration_minutes=10, start_time=time(10, 0))

    assert make_scheduler().detect_conflicts([outer, inner]) == [outer, inner]


def test_unscheduled_and_completed_tasks_are_ignored_by_default_warnings():
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(Task(id="a", title="A", duration_minutes=30, start_time=time(9, 0)))
    pet.add_task(Task(id="b", title="B", duration_minutes=30))  # no start_time
    pet.add_task(Task(id="c", title="C", duration_minutes=30,
                      start_time=time(9, 0), completed=True))

    assert make_scheduler(pet).conflict_warnings() == []


def test_generated_plan_has_no_conflicts():
    pet = Pet(name="Biscuit", species="dog")
    for i, minutes in enumerate((30, 20, 10)):
        pet.add_task(Task(id=f"t{i}", title=f"Task {i}", duration_minutes=minutes))
    scheduler = make_scheduler(pet)

    plan = scheduler.generate_daily_plan()

    assert len(plan) == 3
    assert scheduler.detect_conflicts(plan) == []
