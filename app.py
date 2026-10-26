from datetime import date

import streamlit as st

from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

PRIORITY_BADGE = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}
SPECIES_ICON = {"dog": "🐶", "cat": "🐱"}


def badge(priority: str) -> str:
    return PRIORITY_BADGE.get(priority.lower(), priority)


def pet_label(name: str, owner: Owner) -> str:
    pet = next((p for p in owner.pets if p.name == name), None)
    return f"{SPECIES_ICON.get(pet.species, '🐾') if pet else '🐾'} {name}"


st.title("🐾 PawPal+")
st.caption("A daily care planner: prioritises tasks, fits them into your time, "
           "and warns you about overlaps.")

st.divider()

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)
owner: Owner = st.session_state.owner

# ---------------------------------------------------------------- Owner
st.subheader("👤 Owner")
c1, c2 = st.columns(2)
with c1:
    owner.name = st.text_input("Owner name", value=owner.name)
with c2:
    owner.available_minutes = int(
        st.number_input("Minutes available today", min_value=0, max_value=1440,
                        value=owner.available_minutes, step=15)
    )

# ---------------------------------------------------------------- Pets
st.subheader("🐕 Pets")
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
        st.success(f"Added {pet_name.strip()} to the household.")

if owner.pets:
    st.table([{"Pet": pet_label(p.name, owner), "Species": p.species.title(),
               "Age": p.age, "Tasks": len(p.tasks)} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

# ---------------------------------------------------------------- Add task
st.subheader("📝 Add a Task")
if owner.pets:
    target_name = st.selectbox("Pet", [p.name for p in owner.pets])
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2,
                                format_func=badge)
    with col4:
        recurrence = st.selectbox("Repeats", ["none", "daily", "weekly"],
                                  format_func=str.title)

    if st.button("Add task"):
        pet = next(p for p in owner.pets if p.name == target_name)
        st.session_state.task_counter = st.session_state.get("task_counter", 0) + 1
        try:
            pet.add_task(Task(id=f"t{st.session_state.task_counter}", title=task_title,
                              duration_minutes=int(duration), priority=priority,
                              recurrence=recurrence, due_date=date.today()))
            st.success(f"Added '{task_title}' to {pet.name}.")
        except ValueError as e:
            st.error(str(e))
else:
    st.info("Add a pet before scheduling tasks.")

# ---------------------------------------------------------------- Task list
st.subheader("📋 Task List")
scheduler = Scheduler(owner)
all_tasks = owner.get_all_tasks()

if not all_tasks:
    st.info("No tasks yet. Add one above.")
else:
    f1, f2 = st.columns(2)
    with f1:
        pet_filter = st.selectbox("Filter by pet", ["All"] + [p.name for p in owner.pets])
    with f2:
        status_filter = st.selectbox("Filter by status", ["All", "Pending", "Completed"])

    visible = scheduler.sort_tasks(scheduler.filter_tasks(
        all_tasks,
        completed={"All": None, "Pending": False, "Completed": True}[status_filter],
        pet_name=None if pet_filter == "All" else pet_filter,
    ))

    m1, m2, m3 = st.columns(3)
    m1.metric("Showing", f"{len(visible)} of {len(all_tasks)}")
    m2.metric("Pending", sum(1 for t in visible if not t.completed))
    m3.metric("Total minutes", sum(t.duration_minutes for t in visible))

    if visible:
        st.caption("Sorted by priority (high first), then shortest duration.")
        st.table([{
            "Status": "✅ Done" if t.completed else "⏳ Pending",
            "Pet": pet_label(t.pet_name, owner),
            "Task": t.title,
            "Priority": badge(t.priority),
            "Minutes": t.duration_minutes,
            "Repeats": t.recurrence.title(),
            "Due": t.due_date.strftime("%b %d") if t.due_date else "—",
        } for t in visible])
    else:
        st.warning("No tasks match those filters.")

    pending = scheduler.filter_tasks(all_tasks, completed=False)
    if pending:
        with st.expander("✔️ Mark a task complete"):
            labels = {f"{t.title} — {t.pet_name} ({t.id})": t for t in pending}
            choice = st.selectbox("Task", list(labels))
            if st.button("Complete task"):
                done = labels[choice]
                following = scheduler.complete_task(done.pet_name, done.id)
                if following:
                    st.session_state.flash = (
                        f"Completed '{done.title}'. Next {following.recurrence} "
                        f"occurrence scheduled for {following.due_date:%A, %b %d}.")
                else:
                    st.session_state.flash = f"Completed '{done.title}'."
                st.rerun()

    # Overlaps among tasks that already have start times; informational only.
    overlap_warnings = scheduler.conflict_warnings()
    if overlap_warnings:
        st.warning("**Scheduling conflicts detected**\n\n"
                   + "\n\n".join(f"- {w.removeprefix('WARNING: ')}" for w in overlap_warnings))

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

st.divider()

# ---------------------------------------------------------------- Schedule
st.subheader("📅 Today's Schedule")
if st.button("Generate schedule", type="primary"):
    plan = scheduler.generate_daily_plan()
    if not plan:
        st.warning("Nothing could be scheduled. Add tasks or increase available minutes.")
    else:
        used = sum(t.duration_minutes for t in plan)
        m1, m2, m3 = st.columns(3)
        m1.metric("Tasks scheduled", len(plan))
        m2.metric("Time used", f"{used} / {owner.available_minutes} min")
        m3.metric("Skipped", len(scheduler.skipped))

        st.table([{
            "Time": f"{t.start_time:%H:%M} – {t.end_time:%H:%M}",
            "Pet": pet_label(t.pet_name, owner),
            "Task": t.title,
            "Priority": badge(t.priority),
            "Minutes": t.duration_minutes,
        } for t in scheduler.sort_by_time(plan)])

        warnings = scheduler.conflict_warnings(plan)
        if warnings:
            for w in warnings:
                st.warning(w.removeprefix("WARNING: "))
        else:
            st.success("No time conflicts in today's plan.")

        with st.expander("Why this plan?"):
            st.text(scheduler.explain_plan(plan))

    if scheduler.skipped:
        st.warning("**Skipped (not enough time left):** "
                   + ", ".join(f"{t.title} ({t.pet_name})" for t in scheduler.skipped))
