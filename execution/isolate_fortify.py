import shutil
import os
import subprocess
import sys

def run_command(command, cwd=None):
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Stderr: {e.stderr}")
        return None

def main():
    source_dir = "/Users/andrickjohn/Projects/Test/Fortify"
    target_dir = "/Users/andrickjohn/Projects/Fortify-Repo"
    
    print(f"Starting isolation of Fortify from {source_dir} to {target_dir}...")

    # 1. Check if target exists
    if os.path.exists(target_dir):
        print(f"Target directory {target_dir} already exists. Aborting to avoid overwrite.")
        sys.exit(1)

    # 2. Copy the directory
    try:
        shutil.copytree(source_dir, target_dir)
        print(f"Copied Fortify to {target_dir}")
    except Exception as e:
        print(f"Failed to copy directory: {e}")
        sys.exit(1)

    # 3. Copy .gitignore from root if it exists, merging with Fortify's if needed
    root_gitignore = "/Users/andrickjohn/Projects/Test/.gitignore"
    target_gitignore = os.path.join(target_dir, ".gitignore")
    
    if os.path.exists(root_gitignore):
        try:
            with open(root_gitignore, 'r') as f:
                root_content = f.read()
            
            # If target has .gitignore, append root content or merge?
            # Usually project specific gitignore is better. Fortify usually has one.
            # Let's check if Fortify has one.
            if os.path.exists(target_gitignore):
                print("Fortify already has a .gitignore. Appending root ignore patterns just in case (commented out).")
                with open(target_gitignore, 'a') as f:
                    f.write("\n# Inherited from monorepo root .gitignore\n")
                    f.write(root_content)
            else:
                shutil.copy(root_gitignore, target_gitignore)
                print(f"Copied root .gitignore to {target_gitignore}")
        except Exception as e:
            print(f"Warning: Failed to process .gitignore: {e}")

    # 4. Initialize Git in the new repo
    print("Initializing new git repository...")
    run_command(["git", "init"], cwd=target_dir)
    run_command(["git", "add", "."], cwd=target_dir)
    run_command(["git", "commit", "-m", "Initial commit: Isolated Fortify from monorepo"], cwd=target_dir)
    
    print(f"Successfully created separate repository at {target_dir}")
    print("Next steps:")
    print("1. cd " + target_dir)
    print("2. git remote add origin <NEW_REPO_URL>")
    print("3. git push -u origin main")

if __name__ == "__main__":
    main()
