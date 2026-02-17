# Multi-Machine Sync Notes

## Philosophy
This workspace is designed to seamlessly transition between your Home and Office Macs using Git as the bridge.

## Sync Protocol

### Starting a Session
1. Run `/hello` to pull latest changes and initialize the workspace
2. The system will sync from `origin main` and read all directives

### During Work
- Use `/sync` anytime to save current progress to GitHub
- All work should be incrementally committed

### Ending a Session
1. Run `/goodbye` to:
   - Final sync all changes
   - Document what was accomplished
   - Prepare the workspace for the next machine

## Key Principles
- **Standardization:** Use `uv` for environment management to keep both machines identical
- **Proof of State:** Never trust generated text - always verify with tool output
- **Self-Anneal:** Learn from errors and update directives with new knowledge

## Quick Commands
| Command | Purpose |
|---------|---------|
| `/hello` | Start session, sync state |
| `/sync` | Manual save to cloud |
| `/goodbye` | End session, document & push |
