# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- 3 core actions a user should be able to do: See today's pet care tasks, consider time availability when prioritizing a task, and producing a daily plan when prompted
- Briefly describe your initial UML design.
  - My UML diagram included 4 classes: Pet, Task, Scheduler, and Owner. Owner has one to many Pets, Pets needs Tasks, Scheduler plans for Owner, and Scheduler orders and selects Tasks.
- What classes did you include, and what responsibilities did you assign to each?
  FoOwner has the responsibilities: It can add a pet, get all tasks across all pets, and list pets. 
  - Pet responsibilities: Can manage its own tasks with add_task, remove_task, and edit_task
  - Task responsibilities: It can mark itself complete and report whether it is high priority
  - Scheduler responsibilites: It can generate a daily plan, sort tasks, check if the time fits, detect any conflicts, and explain the plan. 

  - **b. Design changes**

- Did your design change during implementation?
  - Yes
- If yes, describe at least one change and why you made it.
  Task now links back to its Pet. NoThe plan can say who each task is for
  - Added time fields. The fields give each task a time slot, so overlaps can be easier detected. 
- ---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  - Time budget, priority, duration, completion status, overlaps, day start
- How did you decide which constraints mattered most?
  - Using intuition and narrowing down which constraints have the most risk. So time and priority came first since every owner has limited time. Priority is important for things like medication and food. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  - A tradeoff the scheduler makers is being greedy for priority and not overly optimal. When generating the daily plan, it sorts tasks by highest priority first, then places each task in order and skips any that can't fit in the remaining time. It never rearranges afterwards, which can give a worse answer than searching all combinations. 
- Why is that tradeoff reasonable for this scenario?
  - The tradeoff is reasonable because it's a simple rule: priority is more important than doing a couple of tasks. In real life this tradeoff is used as well. Tasks that include medication or feeding should come first before other tasks like grooming, even if it only tasks a couple minutes. Also, if the owner deems the list is wrong, they can easily fix the plan without much to lose. 

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  - I planned, designed, and implemented with Claude for all stages of the project. After each implementation I asked for a summary for understanding of what it did.
- What kinds of prompts or questions were most helpful?
  - Prompts that were very thorough in what I wanted were the most helpful. For example, listing specific areas I wanted to be implemented or using specific design choices/ wording. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  - After asking for a review of the skeleton, it gave a ton of suggestions for improvement, some of which were too complex so I only accepted 2 out of the 8 suggestions first.
- How did you evaluate or verify what the AI suggested?
  - I verified what the AI suggested by using my own reasoning and understanding of how the code works and overall what the system requirements/goals are to make sure they fit. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  - I tested four types of tests: basic, sorting, recurrence, and conflict detection tests. 
- Why were these tests important?
  - These tests were important because: basic tests are foundational to every other behavior. Sorting tests make sure methods like sort_by_time returns chronological order and unscheduled tasks are last. It also makes sure there's no crashes for things like empty inputs. Recurrence tests are important because creating new data can sometimes add wrong, duplicate, or misdated tasks that the user might not notice. It's important to make sure date math and repeat completion are 100% working as intended. Conflict detection tests are important because it's a huge risk for an owner if something like a double-booked plan is generated. Checking that generated plans never conflict makes sure that the planner and checker agree. 

**b. Confidence**

- How confident are you that your scheduler works correctly?
  - I'm pretty confident the scheduler works correctly. 
- What edge cases would you test next if you had more time?
  - Things like zero or negative durations, making sure the UI buttons work as intended

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  - I'm most satisfied with the testing portion. I think it's really fleshed out and acts as a sanity check for any future updates that might break originally working behavior.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  - I think I would improve the logic behind the system, specifically the number of classes and overall just plan more with the UML diagram beforehand. I know that it's easier to look back and see what should have changed, but I think writing out a plan would be beneficial. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  - Designing systems takes a lot of thinking not just about one part but the whole, overarching goals/requirements in tandem. It's a fine line between knowing what the nitty gritty code is doing and making sure it works, is readable, and isn't too complex while making sure it fits the original goal you set. 

## 6. AI Strategy

**a. Which AI coding assistant features were most effective for building your scheduler?**
- The ability to give the AI assistant a nudge on what file/parts of a file to read before writing anything. It also was able to use bash to run things to verify, such as the pytests.

**b. Give one example of an AI suggestion you rejected or modified to keep your system design clean.**
- I modified a suggestion of the AI when it was implementing features of the pawpal system. It came up with complex features that weren't necessarily needed right now, so I modified it to cut down to only 4 new features that were simpler. 


**c. How did using separate chat sessions for different phases help you stay organized?**
- It gave a clear context window of what I was trying to achieve for less hallucination/working in places that was not needed. For example, a new chat after designing the uml diagram, implementing the method stubs, then writing the test cases made it so I could go back to each chat if I wanted to continue writing more tests or continue implementing features. 