---
description: Document session and securely push all work to repository
---

# Goodbye Workflow
**Goal:** Document the session and securely push all work to the repository.

**Instructions:**
// turbo
1. **Sync Agent Files:** Execute `python3 execution/sync_agent_files.py` to ensure all agent instruction files are synchronized before commit.
2. **Final Sync:** Run `python execution/git_sync.py "End of Session: [Brief Summary of Work]"`.
3. **Session Summary:** Write a 3-bullet summary in the chat of:
   - What features were added or fixed.
   - Any new "Learnings" added to the `directives/`.
   - The specific "next step" for the next session.
4. **Verification:** Confirm that the local workspace is clean and pushed to `origin main`.
5. **Sign Off:** "Workspace saved. Everything is ready for your other Mac. Aloha!"
