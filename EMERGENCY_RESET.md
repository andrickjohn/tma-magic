# EMERGENCY RESET PROTOCOL
**FILENAME:** `EMERGENCY_RESET.md`
**LAST UPDATED:** 2026-02-03
**STATUS:** CRITICAL / DESTRUCTIVE

---

## ⚠️ WARNING: READ BEFORE PROCEEDING
**These commands are destructive.** They are designed to wipe away all current work, uncommitted changes, and untracked files to return the repository to a known "perfect" baseline state. **There is no undo.**

---

## Scenario A: The Current Environment is Broken
If your agent configurations, scripts, or workspace have become "out of whack" and you want to **wipe everything** and return to the clean installation state.

### 1. Hard Reset to Baseline (Destructive)
Run these commands from the root of the project (`/Users/john/Projects/test`):

```zsh
# 1. Remove all untracked files and directories (d = directories, f = force, x = ignored files too)
git clean -fdx

# 2. Reset the current branch to match the 'template-base' cleanly
git fetch origin
git reset --hard origin/template-base
```
*Note: This puts you on the clean "template" state. If you want to keep your current branch history but just reset files, use `git reset --hard baseline-v1`.*

### 2. Restore "Main" (If you just messed up the latest work)
If you just want to discard recent changes but keep the project history:
```zsh
git reset --hard origin/main
```

---

## Scenario B: Creating a NEW Project from Scratch
If you want to start a brand new project using the clean agent environment (without the "TMA Project" data or other history).

### Option 1: Using the Template Branch
1. Clone the repository to a new folder:
   ```zsh
   git clone https://github.com/andrickjohn/Test.git my-new-project
   cd my-new-project
   ```
2. Checkout the clean template:
   ```zsh
   git checkout template-base
   ```
3. Create a new main branch for this new project:
   ```zsh
   git checkout -b main
   ```
   *You now have a fresh project with only the core agent files (GEMINI.md, .agents workflows, etc).*

---

## Artifacts Reference
- **Tag `baseline-v1`**: A snapshot of the repo exactly as it was when the environment was verified working.
- **Branch `template-base`**: An orphan branch containing *only* the environment files (no project data).
