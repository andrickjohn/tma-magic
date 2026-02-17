#!/usr/bin/env python3
"""
Sync Agent Instruction Files
=============================
Maintains a single source of truth for agent instructions.

This script copies agents.md to GEMINI.md and CLAUDE.md to ensure
all AI models receive identical instructions regardless of which
model is active in Antigravity.

Usage:
    python execution/sync_agent_files.py

The script is called automatically by:
    - /hello workflow (on session start)
    - /goodbye workflow (before push)
"""

import shutil
import hashlib
from pathlib import Path
from datetime import datetime

def get_file_hash(filepath: Path) -> str:
    """Get MD5 hash of file contents."""
    if not filepath.exists():
        return ""
    return hashlib.md5(filepath.read_bytes()).hexdigest()

def sync_agent_files():
    """Sync agents.md to GEMINI.md and CLAUDE.md."""
    root = Path(__file__).parent.parent
    source = root / ".agent/rules/agents.md"
    targets = [root / "GEMINI.md", root / "CLAUDE.md"]
    
    if not source.exists():
        print(f"❌ Source file not found: {source}")
        return False
    
    source_hash = get_file_hash(source)
    changes_made = []
    already_synced = []
    
    for target in targets:
        target_hash = get_file_hash(target)
        
        if source_hash == target_hash:
            already_synced.append(target.name)
        else:
            shutil.copy(source, target)
            changes_made.append(target.name)
    
    # Report results
    print(f"🔄 Agent File Sync — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Source: agents.md ({source_hash[:8]}...)")
    
    if changes_made:
        for name in changes_made:
            print(f"   ✅ Updated: {name}")
    
    if already_synced:
        for name in already_synced:
            print(f"   ✓ Already in sync: {name}")
    
    if not changes_made:
        print("   📋 All files already synchronized.")
    
    return True

if __name__ == "__main__":
    sync_agent_files()
