#!/bin/bash
# Get current commit message
ORIG_MSG=$(git log --format=%B -n 1 HEAD)

# Translate it
NEW_MSG=$(echo "$ORIG_MSG" | python translate_commit.py)

# Only amend if it changed
if [ "$ORIG_MSG" != "$NEW_MSG" ]; then
    # Save to temp file to preserve formatting
    echo "$NEW_MSG" > /tmp/new_commit_msg.txt
    git commit --amend -F /tmp/new_commit_msg.txt
    rm -f /tmp/new_commit_msg.txt
fi

exit 0
