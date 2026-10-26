from pawpal_system import Pet, Task


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
