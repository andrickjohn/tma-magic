#!/bin/bash

# USAGE: ./create_project.sh "Project Name"
# Example: ./create_project.sh "New Stuff"

PROJECT_NAME="$1"

if [ -z "$PROJECT_NAME" ]; then
  echo "Error: Please provide a project name."
  echo "Usage: ./create_project.sh \"My New Project\""
  exit 1
fi

# 1. Define Paths
PARENT_DIR="/Users/john/Projects"
TARGET_DIR="$PARENT_DIR/$PROJECT_NAME"

echo "🚀 Starting new project setup: '$PROJECT_NAME'..."

# 2. Check if folder exists
if [ -d "$TARGET_DIR" ]; then
  echo "❌ Error: Directory '$TARGET_DIR' already exists."
  exit 1
fi

# 3. Clone the Template (specifically the 'template-base' branch)
echo "📦 Cloning template-base..."
git clone --branch template-base https://github.com/andrickjohn/Test.git "$TARGET_DIR"

if [ $? -ne 0 ]; then
    echo "❌ Clone failed."
    exit 1
fi

cd "$TARGET_DIR" || exit

# 4. Create new 'main' branch and clean up
echo "🧹 Formatting branches..."
git checkout -b main
git remote remove origin

# 5. Create new GitHub Repo using 'gh'
echo "🌐 Creating private repository on GitHub..."
# Create repo, ensuring name is sanitized for URL if needed (gh handles quotes usually)
# We use --source=. to immediately link this current folder to the new repo
gh repo create "$PROJECT_NAME" --private --source=. --push

if [ $? -eq 0 ]; then
    echo "✅ Success! Project '$PROJECT_NAME' is ready."
    echo "📂 Location: $TARGET_DIR"
    echo "🔗 GitHub: https://github.com/andrickjohn/$(echo "$PROJECT_NAME" | tr ' ' '-')"
else
    echo "❌ Failed to create GitHub repository. Checks:"
    echo "   - Are you logged in? (Run 'gh auth login')"
    echo "   - Does the repo already exist?"
fi
