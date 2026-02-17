# Learnings

Accumulated knowledge from errors, edge cases, and discoveries.
These persist across sessions to prevent repeating mistakes.

---

## Git & Version Control

### 2026-02-03: Empty Folders Not Tracked
**Context:** User created a folder called "TMA Project" but `/sync` didn't push it to GitHub.

**Root Cause:** Git only tracks files, not directories. Empty folders are invisible to Git.

**Solution:** Add a placeholder file (`.gitkeep`) inside empty folders you want tracked.

**Prevention:** When creating project folders, automatically add `.gitkeep` if the folder is meant to be preserved but has no content yet.

---

## Performance & System Health

### 2026-02-09: Large Directory Stalls
**Context:** Agent was "getting stuck" or running very slowly on search/grep operations.

**Root Cause:** The project contains large directories like `Fortify/node_modules` (899M) and `Fortify/.next/` which were being indexed during broad searches.

**Solution:** Updated global instructions to explicitly exclude these directories in all tool calls.

**Prevention:** Always use the `Excludes` parameter in `find_by_name` and `Includes` (with exclusion patterns) in `grep_search`. Monitor background processes for long-running CLI sessions that might be consuming resources.

### 2026-02-13: Monorepo Deployment Conflict
**Context:** A user adding `TMA Project` introduced a root `vercel.json` that hijacked the `Fortify` Vercel deployment, causing a 404.

**Root Cause:** Vercel treats a root `vercel.json` as the source of truth for the *entire* repository, overriding project-specific settings in the UI.

**Solution:** Deleted root `vercel.json`. Configured Vercel UI "Root Directory" to point explicitly to `Fortify`.

**Prevention:** NEVER create a `vercel.json` or deployment config in the root of this monorepo. Deployment configs must live strictly inside their respective project subdirectories (e.g., `Fortify/vercel.json`).

### 2026-02-10: Agent Directory Naming
**Context:** Confusion between `.agent` and `.agents` caused workflow discovery issues.

**Root Cause:** Inconsistent naming. System tools expect `.agent` (singular) as defined in `GEMINI.md`.

**Solution:** Renamed `.agents` to `.agent`.

**Prevention:** ALWAYS use `.agent` (singular) for the agent configuration directory.


```
### YYYY-MM-DD: [Short Title]
**Context:** [What was the user trying to do?]

**Root Cause:** [Why did it fail or behave unexpectedly?]

**Solution:** [What fixed it?]

**Prevention:** [How to avoid this in the future?]
```
