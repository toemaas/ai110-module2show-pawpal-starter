from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=90, day_start=time(7, 30))

    biscuit = Pet(name="Biscuit", species="dog", age=4)
    mia = Pet(name="Mia", species="cat", age=2)
    owner.add_pet(biscuit)
    owner.add_pet(mia)

    biscuit.add_task(Task(id="b1", title="Morning walk", duration_minutes=30, priority="high", category="exercise"))
    biscuit.add_task(Task(id="b2", title="Brush coat", duration_minutes=20, priority="low", category="grooming"))
    mia.add_task(Task(id="m1", title="Breakfast", duration_minutes=10, priority="high", category="feeding"))
    mia.add_task(Task(id="m2", title="Give medication", duration_minutes=5, priority="high", category="meds"))
    mia.add_task(Task(id="m3", title="Laser pointer play", duration_minutes=25, priority="medium", category="enrichment"))

    scheduler = Scheduler(owner)
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
