from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=90, day_start=time(7, 30))

    biscuit = Pet(name="Biscuit", species="dog", age=4)
    mia = Pet(name="Mia", species="cat", age=2)
    owner.add_pet(biscuit)
    owner.add_pet(mia)

    # Added deliberately out of chronological order; b3 has no start time.
    biscuit.add_task(Task(id="b1", title="Evening walk", duration_minutes=30, priority="high", category="exercise", start_time=time(18, 0)))
    biscuit.add_task(Task(id="b2", title="Brush coat", duration_minutes=20, priority="low", category="grooming", start_time=time(12, 30)))
    biscuit.add_task(Task(id="b3", title="Training session", duration_minutes=15, priority="medium", category="training"))
    mia.add_task(Task(id="m1", title="Breakfast", duration_minutes=10, priority="high", category="feeding", start_time=time(7, 30)))
    mia.add_task(Task(id="m2", title="Give medication", duration_minutes=5, priority="high", category="meds", start_time=time(9, 0)))
    mia.add_task(Task(id="m3", title="Laser pointer play", duration_minutes=25, priority="medium", category="enrichment", start_time=time(15, 15)))
    mia.tasks[1].mark_complete()  # medication already given

    scheduler = Scheduler(owner)
    all_tasks = owner.get_all_tasks()

    def show(label: str, tasks: list[Task]) -> None:
        print(f"\n{label}")
        for t in tasks:
            start = t.start_time.strftime("%H:%M") if t.start_time else "--:--"
            status = "done" if t.completed else "todo"
            print(f"  {start}  {t.title:<20} {t.pet_name:<8} {status}")

    print("=" * 50)
    print("Sorting & filtering demo")
    print("=" * 50)
    show("As added (out of order):", all_tasks)
    show("sort_by_time:", scheduler.sort_by_time(all_tasks))
    show("filter completed=True:", scheduler.filter_tasks(all_tasks, completed=True))
    show("filter completed=False:", scheduler.filter_tasks(all_tasks, completed=False))
    show("filter pet_name='mia' (case-insensitive):", scheduler.filter_tasks(all_tasks, pet_name="mia"))
    show("filter Biscuit + todo, sorted by time:",
         scheduler.sort_by_time(scheduler.filter_tasks(all_tasks, completed=False, pet_name="Biscuit")))
    print()

    print("=" * 50)
    print("Conflict warning demo")
    print("=" * 50)
    clash_tasks = [
        Task(id="x1", title="Vet visit", duration_minutes=60, pet_name="Biscuit", start_time=time(10, 0)),
        Task(id="x2", title="Nail trim", duration_minutes=15, pet_name="Biscuit", start_time=time(10, 30)),
        Task(id="x3", title="Vaccination", duration_minutes=30, pet_name="Mia", start_time=time(10, 0)),
        Task(id="x4", title="Lunch", duration_minutes=10, pet_name="Mia", start_time=time(12, 0)),
        Task(id="x5", title="Unscheduled play", duration_minutes=20, pet_name="Mia"),
    ]
    for line in scheduler.conflict_warnings(clash_tasks) or ["No conflicts."]:
        print(f"  {line}")
    print("  Current pending tasks:", scheduler.conflict_warnings() or "no conflicts")

    # Two real tasks (one per pet) booked at exactly the same time.
    biscuit.add_task(Task(id="c1", title="Grooming appointment", duration_minutes=30, start_time=time(14, 0)))
    mia.add_task(Task(id="c2", title="Vet checkup", duration_minutes=30, start_time=time(14, 0)))
    print("\n  After adding two tasks at 14:00:")
    warnings = scheduler.conflict_warnings()
    for line in warnings or ["No conflicts."]:
        print(f"  {line}")
    assert len(warnings) == 1 and "Grooming appointment" in warnings[0] and "Vet checkup" in warnings[0]
    print("  OK: same-time conflict detected.")
    biscuit.remove_task("c1")  # keep the later plan demo unchanged
    mia.remove_task("c2")
    print()

    print("=" * 50)
    print("Recurring task demo")
    print("=" * 50)
    biscuit.add_task(Task(id="b4", title="Flea medicine", duration_minutes=5, recurrence="weekly"))
    mia.add_task(Task(id="m4", title="Feed dinner", duration_minutes=10, recurrence="daily"))
    for pet, tid in [("Mia", "m4"), ("Biscuit", "b4"), ("Biscuit", "b2")]:
        nxt = scheduler.complete_task(pet, tid)
        if nxt:
            print(f"  Completed {tid} -> new '{nxt.title}' id={nxt.id} due {nxt.due_date}")
        else:
            print(f"  Completed {tid} -> no recurrence, nothing created")
    print()

    plan = scheduler.generate_daily_plan()

    print("=" * 50)
    print("Today's Schedule")
    print("=" * 50)
    print(scheduler.explain_plan(plan))

    conflicts = scheduler.detect_conflicts(plan)
    if conflicts:
        print("\nConflicts: " + ", ".join(t.title for t in conflicts))


if __name__ == "__main__":
    main()
