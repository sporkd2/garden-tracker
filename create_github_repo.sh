#!/bin/bash

# Script to create a GitHub repository and push code
# This requires a GitHub Personal Access Token

REPO_NAME="garden-tracker"
REPO_DESCRIPTION="A beautiful Flask-based web application for tracking garden plants, watering schedules, and garden bed layouts"

echo "🌱 Garden Tracker - GitHub Repository Setup"
echo "==========================================="
echo ""
echo "This script will create a new GitHub repository and push your code."
echo ""
echo "You'll need a GitHub Personal Access Token with 'repo' scope."
echo "Create one at: https://github.com/settings/tokens/new"
echo ""
read -sp "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
echo ""
echo ""

# Create the repository
echo "Creating repository '$REPO_NAME'..."
RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$REPO_NAME\",\"description\":\"$REPO_DESCRIPTION\",\"private\":false,\"auto_init\":false}" \
  https://api.github.com/user/repos)

# Check if creation was successful
if echo "$RESPONSE" | grep -q "\"full_name\""; then
  REPO_URL=$(echo "$RESPONSE" | grep -o '"clone_url": *"[^"]*"' | sed 's/"clone_url": *"\([^"]*\)"/\1/')
  echo "✅ Repository created successfully!"
  echo "Repository URL: $REPO_URL"
  echo ""

  # Add remote and push
  echo "Adding remote and pushing code..."
  git remote add origin "$REPO_URL"
  git branch -M main
  git push -u origin main

  echo ""
  echo "✅ Code pushed successfully!"
  echo "🌐 View your repository at: https://github.com/$(git config user.name)/$REPO_NAME"
else
  echo "❌ Failed to create repository"
  echo "Response: $RESPONSE"
  exit 1
fi
