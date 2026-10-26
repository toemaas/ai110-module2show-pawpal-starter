import streamlit as st

from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )


st.divider()

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)
owner: Owner = st.session_state.owner

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = int(
    st.number_input("Minutes available today", min_value=0, max_value=1440,
                    value=owner.available_minutes, step=15)
)

st.subheader("Adding a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age", min_value=0, max_value=50, value=1)

if st.button("Add pet"):
    if not pet_name.strip():
        st.error("Pet name is required.")
    elif any(p.name.lower() == pet_name.strip().lower() for p in owner.pets):
        st.error(f"{pet_name} is already in the household.")
    else:
        owner.add_pet(Pet(name=pet_name.strip(), species=species, age=int(age)))
        st.success(f"Added {pet_name}.")

if owner.pets:
    st.table([{"name": p.name, "species": p.species, "age": p.age, "tasks": len(p.tasks)}
              for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.subheader("Scheduling a Task")
if owner.pets:
    target_name = st.selectbox("Pet", [p.name for p in owner.pets])
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        pet = next(p for p in owner.pets if p.name == target_name)
        st.session_state.task_counter = st.session_state.get("task_counter", 0) + 1
        try:
            pet.add_task(Task(id=f"t{st.session_state.task_counter}", title=task_title,
                              duration_minutes=int(duration), priority=priority))
            st.success(f"Added '{task_title}' to {pet.name}.")
        except ValueError as e:
            st.error(str(e))
else:
    st.info("Add a pet before scheduling tasks.")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table([{"pet": t.pet_name, "title": t.title, "duration_minutes": t.duration_minutes,
               "priority": t.priority} for t in all_tasks])

st.divider()

st.subheader("Build Schedule")
if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan()
    if not plan:
        st.warning("Nothing could be scheduled. Add tasks or increase available minutes.")
    else:
        st.table([{"start": t.start_time.strftime("%H:%M"), "pet": t.pet_name,
                   "task": t.title, "minutes": t.duration_minutes, "priority": t.priority}
                  for t in plan])
        conflicts = scheduler.detect_conflicts(plan)
        if conflicts:
            st.error("Conflicts: " + ", ".join(t.title for t in conflicts))
        st.text(scheduler.explain_plan(plan))
    for t in scheduler.skipped:
        st.warning(f"Skipped (not enough time): {t.title} ({t.pet_name})")
