#!/bin/bash

# Check if repo is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <owner/repo>"
  echo "Example: $0 actions/checkout"
  exit 1
fi

REPO=$1
API_URL="https://api.github.com/repos/$REPO/releases/latest"

echo "Fetching latest release for $REPO..."

# Use curl to get the latest release data from GitHub API
RESPONSE=$(curl -s $API_URL)

# Extract the tag_name using grep and cut
TAG_NAME=$(echo "$RESPONSE" | grep -o '"tag_name": *"[^"]*"' | cut -d '"' -f 4)

if [ -z "$TAG_NAME" ] || [ "$TAG_NAME" = "null" ]; then
    # Sometimes repositories use tags instead of formal releases
    echo "No formal release found. Trying to fetch latest tag..."
    TAGS_URL="https://api.github.com/repos/$REPO/tags"
    TAGS_RESPONSE=$(curl -s $TAGS_URL)
    TAG_NAME=$(echo "$TAGS_RESPONSE" | grep -o '"name": *"[^"]*"' | head -n 1 | cut -d '"' -f 4)
    
    if [ -z "$TAG_NAME" ] || [ "$TAG_NAME" = "null" ]; then
        echo "Failed to fetch latest release or tag. Repository might not have them or is private."
        exit 1
    fi
fi

echo "Latest release/tag for $REPO is: $TAG_NAME"
