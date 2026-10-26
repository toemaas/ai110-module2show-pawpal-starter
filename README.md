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


## ✨ Features

All scheduling logic is in `pawpal_system.py`.

- **Multi-pet planning.** `Owner.get_all_tasks()` flattens every pet's tasks, so one plan covers the whole household. Each task carries its pet's name.
- **Priority-then-duration sorting** (`sort_tasks`). Tasks sort by priority rank (high=3, medium=2, low=1, anything unrecognised=0), then by shortest duration. The sort is stable, so full ties keep their original order. It returns a new list and never mutates its input.
- **Greedy time-budget planner** (`generate_daily_plan`). It drops completed tasks, sorts the rest, then walks the list once against `available_minutes`. A task that fits is assigned a start time and placed back to back, beginning at `day_start`. A task that does not fit is skipped, but later and shorter tasks are still tried, so leftover time gets used. Skipped tasks are kept in `scheduler.skipped` and have their `start_time` cleared. Any preset `start_time` is overwritten.
- **Chronological sorting** (`sort_by_time`). Orders by `start_time`, earliest first, with unscheduled tasks last. A task at 00:00 counts as scheduled.
- **Filtering** (`filter_tasks`). Filters by completion status and/or pet name. Pet names match case-insensitively, a filter set to `None` is skipped, and filters combine with AND.
- **Conflict warnings** (`conflict_warnings`). A sweep over tasks sorted by start time, tracking which timed tasks are still running. Every overlapping pair produces a message with both time ranges, labelled "same pet" or "different pets". It defaults to all pending tasks, ignores unscheduled ones, and never raises or blocks scheduling.
- **Conflict detection** (`detect_conflicts`). Compares every pair of timed tasks in a plan using the interval test `a.start < b.end and b.start < a.end`. Back-to-back tasks (09:00-09:30 then 09:30-10:00) are not a conflict. It returns each overlapping `Task` once.
- **Recurring tasks** (`Task.next_occurrence`, `Scheduler.complete_task`). Completing a `daily` or `weekly` task (case-insensitive) creates a pending copy due 1 or 7 days after the task's `due_date` (today if unset). The copy gets the id `<base id>@<YYYY-MM-DD>`, keeps its other fields, and has `start_time` cleared. Completing an already-completed task does nothing, so no duplicate is created. Other recurrence values, including `none`, create no copy.
- **Safe task management.** `Pet.add_task` rejects duplicate ids, `remove_task` and `complete_task` raise `KeyError` for unknown ids or pets, and `edit_task` rejects unknown fields and refuses to change `id` or `pet_name`.
- **Plan explanation** (`explain_plan`). Prints each slot with pet, duration and priority, states the ordering rule, reports minutes used, and lists skipped tasks.

## 🧪 Testing PawPal+
The tests cover four areas:  
Basics: marking a task complete, and adding tasks to a pet
Sorting: Chronological order by start time, unscheduled tasks last, tiebreaker ordering, etc.
Recurrence: Daily and weekly follow-ups with the right due date, leap-day rollover, duplicates, etc.
Conflicts:  Duplicate start times, same pets but different pet labels, completed and unscheduled tasks ignored
## Confidence Level: 4 stars
```bash
# Run the full test suite:
python -m pytest

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
collected 23 items                                                                                                                                                                                                                         

tests\test_pawpal.py ..                                                                                                                                                                                                             [100%]

==================================== 23 passed in 0.04s ==================================================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Daily plan | `Scheduler.generate_daily_plan` | Greedy: places pending tasks from `day_start` until `available_minutes` runs out; tasks that don't fit go to `Scheduler.skipped`. |
| Priority sorting | `Scheduler.sort_tasks` | High priority first, then shortest duration first. |
| Time sorting | `Scheduler.sort_by_time` | Orders tasks by `start_time`, earliest first; unscheduled tasks go last. |
| Filtering | `Scheduler.filter_tasks` | Filter by completion status and/or pet name (case-insensitive); filters can be combined. |
| Time-fit check | `Scheduler.fits_in_time` | Tests whether a task's duration fits the minutes remaining. |
| Conflict warnings | `Scheduler.conflict_warnings` | Returns a warning string for each overlapping pair of timed tasks, same pet or different pets. Never raises. |
| Conflict detection | `Scheduler.detect_conflicts` | Returns the overlapping `Task` objects themselves. |
| Recurring tasks | `Task.next_occurrence`, `Scheduler.complete_task` | Completing a "daily" or "weekly" task creates a new copy due 1 or 7 days later, with id `<id>@<due date>`. |
| Plan explanation | `Scheduler.explain_plan` | Readable schedule showing the ordering rule, time used, and skipped tasks. |

Run `python main.py` to see sorting, filtering, conflict warnings and recurrence demonstrated in the terminal.

**Known limitations:** the planner overwrites any preset `start_time`, does not filter by `due_date`, and does not use `Owner.preferences`.

## 📸 Demo Walkthrough

### The Streamlit app (`streamlit run app.py`)

**What you can do**

| Section | Actions |
|---------|---------|
| Owner | Set your name and the minutes you have available today. |
| Pets | Add pets (name, species, age). Duplicate names are rejected. A summary table shows each pet's task count. |
| Add a Task | Pick a pet, then set title, duration, priority and how often it repeats (none, daily, weekly). |
| Task List | Filter by pet and by status (pending or completed). Rows are sorted by priority, then shortest first, with summary metrics for the current filter. |
| Mark a task complete | Complete a task. If it repeats, the next occurrence is created and its due date is shown. |
| Today's Schedule | Generate the plan. It shows a time-ordered table, minutes used against minutes available, conflict warnings, skipped tasks, and a "Why this plan?" explanation. |

**Example workflow**

1. Set the owner to "Jordan" with 90 minutes available.
2. Add a pet, "Mia" the cat, then a second pet, "Biscuit" the dog.
3. Add tasks: "Breakfast" (10 min, high, daily) for Mia and "Evening walk" (30 min, high) for Biscuit, plus a few lower-priority ones.
4. In the Task List, filter to Biscuit, or to pending tasks only, and see the table re-sort by priority.
5. Mark "Breakfast" complete. A success message announces the next daily occurrence, due tomorrow.
6. Click **Generate schedule**. Tasks are placed back to back from `day_start`. Anything that does not fit appears in the skipped warning.

**Scheduler behaviors on display**

- *Sorting:* the task list uses `sort_tasks` and the schedule table uses `sort_by_time`.
- *Filtering:* the pet and status filters call `filter_tasks`.
- *Recurrence:* completing a repeating task calls `complete_task`.
- *Conflict warnings:* the app calls `conflict_warnings` on the plan and on any tasks that already have start times. Because the planner places tasks back to back, the UI normally reports "No time conflicts". The warnings are easiest to see in the CLI demo below.

### The CLI demo (`python main.py`)

`main.py` builds two pets with deliberately out-of-order tasks and walks through each behavior. Due dates depend on the day it is run; this output was captured on 2026-10-26.

```
==================================================
Sorting & filtering demo
==================================================

As added (out of order):
  18:00  Evening walk         Biscuit  todo
  12:30  Brush coat           Biscuit  todo
  --:--  Training session     Biscuit  todo
  07:30  Breakfast            Mia      todo
  09:00  Give medication      Mia      done
  15:15  Laser pointer play   Mia      todo

sort_by_time:
  07:30  Breakfast            Mia      todo
  09:00  Give medication      Mia      done
  12:30  Brush coat           Biscuit  todo
  15:15  Laser pointer play   Mia      todo
  18:00  Evening walk         Biscuit  todo
  --:--  Training session     Biscuit  todo

filter completed=True:
  09:00  Give medication      Mia      done

filter completed=False:
  18:00  Evening walk         Biscuit  todo
  12:30  Brush coat           Biscuit  todo
  --:--  Training session     Biscuit  todo
  07:30  Breakfast            Mia      todo
  15:15  Laser pointer play   Mia      todo

filter pet_name='mia' (case-insensitive):
  07:30  Breakfast            Mia      todo
  09:00  Give medication      Mia      done
  15:15  Laser pointer play   Mia      todo

filter Biscuit + todo, sorted by time:
  12:30  Brush coat           Biscuit  todo
  18:00  Evening walk         Biscuit  todo
  --:--  Training session     Biscuit  todo

==================================================
Conflict warning demo
==================================================
  WARNING: 'Vet visit' [Biscuit] (10:00-11:00) overlaps 'Vaccination' [Mia] (10:00-10:30) (different pets)
  WARNING: 'Vet visit' [Biscuit] (10:00-11:00) overlaps 'Nail trim' [Biscuit] (10:30-10:45) (same pet)
  Current pending tasks: no conflicts

  After adding two tasks at 14:00:
  WARNING: 'Grooming appointment' [Biscuit] (14:00-14:30) overlaps 'Vet checkup' [Mia] (14:00-14:30) (different pets)
  OK: same-time conflict detected.

==================================================
Recurring task demo
==================================================
  Completed m4 -> new 'Feed dinner' id=m4@2026-10-27 due 2026-10-27
  Completed b4 -> new 'Flea medicine' id=b4@2026-11-02 due 2026-11-02
  Completed b2 -> no recurrence, nothing created

==================================================
Today's Schedule
==================================================
Daily plan for Jordan (90 min available):
  07:30 - Breakfast [Mia] (10 min) [priority: high]
  07:40 - Evening walk [Biscuit] (30 min) [priority: high]
  08:10 - Flea medicine [Biscuit] (5 min) [priority: medium]
  08:15 - Feed dinner [Mia] (10 min) [priority: medium]
  08:25 - Training session [Biscuit] (15 min) [priority: medium]
Ordered by priority (high first), then shortest first. Used 70 of 90 min.
Skipped (not enough time left): Laser pointer play (Mia)
```

**What the output shows**

- *Sorting:* `sort_by_time` turns the out-of-order list into chronological order, with "Training session" (no start time) last.
- *Filtering:* completed-only, pending-only, a case-insensitive pet filter (`'mia'` matches Mia), and a combined pet + status filter feeding `sort_by_time`.
- *Conflict warnings:* overlapping pairs are reported with both time ranges and labelled same pet or different pets. Two tasks at exactly 14:00 are flagged, and unscheduled tasks are ignored.
- *Recurrence:* completing a daily task creates `m4@2026-10-27`, a weekly task creates `b4@2026-11-02`, and a non-recurring task creates nothing.
- *Planning:* high-priority tasks come first, then shorter tasks first within a priority. "Laser pointer play" is skipped because the remaining 20 minutes cannot hold its 25. The completed "Give medication" is left out of the plan.
- *Known quirk:* the plan includes "Feed dinner" and "Flea medicine", the copies due tomorrow and next week, because the planner does not yet filter by `due_date`.
