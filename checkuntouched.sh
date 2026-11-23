#!/usr/bin/env bash

# SHA of the initial commit
initial=4349b450bbed7327342c0b66d29cfc370090dc21

# Paste the output of the previous script here
files=$(cat <<'EOF'
newtxtt/enc/txttAec.enc
newtxtt/enc/txttAqec.enc
newtxtt/enc/txttBec.enc
newtxtt/enc/txttBqec.enc
newtxtt/enc/txttCec.enc
newtxtt/enc/txttCqec.enc
newtxtt/enc/txttDec.enc
newtxtt/enc/txttDqec.enc
newtxtt/enc/txttEec.enc
newtxtt/enc/txttEqec.enc
newtxtt/map/newtxtt.map
newtxtt/tfm/tcxbttz.tfm
newtxtt/tfm/tcxbttzsl.tfm
newtxtt/tfm/tcxttz.tfm
newtxtt/tfm/tcxttzsl.tfm
newtxtt/tfm/txttz.tfm
EOF
)

# Verify each file independently using git log
while IFS= read -r file; do
    [[ -z "$file" ]] && continue

    # Find the latest commit affecting this file
    last=$(git log -1 --format=%H HEAD -- "$file")

    if [[ "$last" == "$initial" ]]; then
        printf 'OK: %s\n' "$file"
    else
        printf 'FAIL: %s (last commit: %s)\n' "$file" "$last"
    fi
done <<< "$files"
