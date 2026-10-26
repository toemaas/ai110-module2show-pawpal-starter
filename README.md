# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🛠️ Implementation Summary

The system lives in `pawpal_system.py` and is built from four classes. The UML is in `diagrams/uml.mmd`.

| Class | Role |
|-------|------|
| `Task` | One care activity: title, duration, priority, category, recurrence, completion status, owning pet, and an assigned start time. |
| `Pet` | Holds a pet's details and its own list of tasks (`add_task`, `remove_task`, `edit_task`). |
| `Owner` | Holds the owner's time budget (`available_minutes`), `day_start`, and all pets. `get_all_tasks()` returns every pet's tasks in one list. |
| `Scheduler` | The "brain". Builds the daily plan, checks for conflicts, and explains its choices. |

**How they work together**

1. An `Owner` has many `Pet`s, and each `Pet` has many `Task`s. `Pet.add_task` stamps each task with the pet's name so the plan can say who it is for.
2. `Scheduler` is given an `Owner` and calls `owner.get_all_tasks()`, so it plans across all pets rather than a single one.
3. `generate_daily_plan()` drops completed tasks, sorts the rest (`sort_tasks`: high priority first, shortest first on ties), then walks the list. Each task that passes `fits_in_time` is given a start time, beginning at `day_start` and placed back to back. Tasks that no longer fit are collected in `scheduler.skipped`.
4. `detect_conflicts()` flags tasks with overlapping time slots, and `explain_plan()` returns a readable schedule with the ordering rule and any skipped tasks.


## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
==================================================
Today's Schedule
==================================================
Daily plan for Jordan (90 min available):
  07:30 - Give medication [Mia] (5 min) [priority: high]
  07:35 - Breakfast [Mia] (10 min) [priority: high]
  07:45 - Morning walk [Biscuit] (30 min) [priority: high]
  08:15 - Laser pointer play [Mia] (25 min) [priority: medium]
  08:40 - Brush coat [Biscuit] (20 min) [priority: low]
Ordered by priority (high first), then shortest first. Used 90 of 90 min.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
=================================== test session starts ============================================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\godca\CodePath\ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 2 items                                                                                                                                                                                                                         

tests\test_pawpal.py ..                                                                                                                                                                                                             [100%]

==================================== 2 passed in 0.02s ==================================================
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
