#!/usr/bin/env bash

# SHA of the initial commit
initial=4349b450bbed7327342c0b66d29cfc370090dc21

# Directory to examine (relative to the repository root)
dir="newtxtt"

# List all files present in the directory at the initial commit
git ls-tree -r -z --name-only "$initial" -- "$dir/" |
while IFS= read -r -d '' file; do

    # Check whether any subsequent commit touched this file
    if [[ -z $(git rev-list -1 "$initial..HEAD" -- "$file") ]]; then

        # Print the file if it was never touched again
        printf '%s\n' "$file"

    fi
done

