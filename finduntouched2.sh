#!/usr/bin/env bash

# SHA of the initial commit
initial=4349b450bbed7327342c0b66d29cfc370090dc21

# Directory to examine (relative to the repository root)
dir="newtxtt"

# Examine every file present at the initial commit
git ls-tree -r -z --name-only "$initial" -- "$dir/" |
while IFS= read -r -d '' file; do

    # Find the most recent commit that touched this file
    last=$(git log -1 --format=%H HEAD -- "$file")

    # Output files whose last modifying commit is the initial commit
    if [[ "$last" == "$initial" ]]; then
        printf '%s\n' "$file"
    fi

done
