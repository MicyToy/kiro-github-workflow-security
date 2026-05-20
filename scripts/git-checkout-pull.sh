#!/bin/bash

# Check if branch name is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <branch_name>"
  exit 1
fi

BRANCH_NAME=$1

# Fetch the latest changes from origin
echo "Fetching latest changes..."
git fetch origin

# Check if the branch exists locally
if git show-ref --verify --quiet refs/heads/$BRANCH_NAME; then
  echo "Checking out existing branch: $BRANCH_NAME"
  git checkout $BRANCH_NAME
else
  # Check if branch exists on remote
  if git ls-remote --exit-code --heads origin $BRANCH_NAME >/dev/null 2>&1; then
    echo "Checking out and tracking remote branch: origin/$BRANCH_NAME"
    git checkout -b $BRANCH_NAME origin/$BRANCH_NAME
  else
    echo "Creating new local branch: $BRANCH_NAME"
    git checkout -b $BRANCH_NAME
  fi
fi

# Pull the latest code if tracking a remote branch
if git config --get branch.$BRANCH_NAME.remote > /dev/null; then
    echo "Pulling latest code for $BRANCH_NAME..."
    git pull origin $BRANCH_NAME
else
    echo "Branch $BRANCH_NAME does not track a remote branch yet."
fi

echo "Successfully checked out $BRANCH_NAME"
