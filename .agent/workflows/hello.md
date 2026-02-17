---
description: Initialize workspace and synchronize with latest project state
---

# Hello Workflow
**Goal:** Initialize the workspace and synchronize with the latest project state.

**Instructions:**
// turbo
1. **Sync Agent Files:** Execute `python3 execution/sync_agent_files.py` to ensure all agent instruction files are synchronized.
2. **Sync State:** Execute `git pull origin main` to ensure we have the latest updates from the other workstation.
3. **Read Directives:** Read `agents.md`, `directives/critic_directive.md`, and `directives/learnings.md` to refresh operating constraints and accumulated knowledge.
4. **Session Check:** Scan the `.tmp/` and `execution/` folders to see the most recent work.
5. **Check Reminders:** Check if `.tmp/next_session_reminder.json` exists. If it does, read and display its content to the user as a high-priority alert, then delete the file.
6. **Greet User:** Report that the system is synchronized and ask: "System aligned. What are we building today, John?"
