#!/usr/bin/env bash

# List of files whose timestamps must be updated.
# Replace these examples with your actual list.
files=$(cat <<'EOF'
newtxtt/README
newtxtt/doc/newtxtt-1060-2026-11-20.md
newtxtt/doc/newtxtt-doc.pdf
newtxtt/doc/newtxtt-doc.tex
newtxtt/enc/tcxAec.enc
newtxtt/enc/tcxBec.enc
newtxtt/enc/tcxCec.enc
newtxtt/enc/tcxDec.enc
newtxtt/enc/tcxEec.enc
newtxtt/tex/newtxtt-ts1-unicode.tex
newtxtt/tex/newtxtt.sty
newtxtt/tex/t1newtxtt.fd
newtxtt/tex/t1newtxttz.fd
newtxtt/tex/ts1newtxtt.fd
newtxtt/tex/ts1newtxttz.fd
newtxtt/tfm/newtcxbsla.tfm
newtxtt/tfm/newtcxbslb.tfm
newtxtt/tfm/newtcxbslc.tfm
newtxtt/tfm/newtcxbsld.tfm
newtxtt/tfm/newtcxbsle.tfm
newtxtt/tfm/newtcxbtta.tfm
newtxtt/tfm/newtcxbttb.tfm
newtxtt/tfm/newtcxbttc.tfm
newtxtt/tfm/newtcxbttd.tfm
newtxtt/tfm/newtcxbtte.tfm
newtxtt/tfm/newtcxsla.tfm
newtxtt/tfm/newtcxslb.tfm
newtxtt/tfm/newtcxslc.tfm
newtxtt/tfm/newtcxsld.tfm
newtxtt/tfm/newtcxsle.tfm
newtxtt/tfm/newtcxtta.tfm
newtxtt/tfm/newtcxttb.tfm
newtxtt/tfm/newtcxttc.tfm
newtxtt/tfm/newtcxttd.tfm
newtxtt/tfm/newtcxtte.tfm
newtxtt/tfm/newtxbtta.tfm
newtxtt/tfm/newtxbttaq.tfm
newtxtt/tfm/newtxbttb.tfm
newtxtt/tfm/newtxbttbq.tfm
newtxtt/tfm/newtxbttc.tfm
newtxtt/tfm/newtxbttcq.tfm
newtxtt/tfm/newtxbttd.tfm
newtxtt/tfm/newtxbttdq.tfm
newtxtt/tfm/newtxbtte.tfm
newtxtt/tfm/newtxbtteq.tfm
newtxtt/tfm/newtxbttsca.tfm
newtxtt/tfm/newtxbttscaq.tfm
newtxtt/tfm/newtxbttscb.tfm
newtxtt/tfm/newtxbttscbq.tfm
newtxtt/tfm/newtxbttscc.tfm
newtxtt/tfm/newtxbttsccq.tfm
newtxtt/tfm/newtxbttscd.tfm
newtxtt/tfm/newtxbttscdq.tfm
newtxtt/tfm/newtxbttsce.tfm
newtxtt/tfm/newtxbttsceq.tfm
newtxtt/tfm/newtxbttsla.tfm
newtxtt/tfm/newtxbttslaq.tfm
newtxtt/tfm/newtxbttslb.tfm
newtxtt/tfm/newtxbttslbq.tfm
newtxtt/tfm/newtxbttslc.tfm
newtxtt/tfm/newtxbttslcq.tfm
newtxtt/tfm/newtxbttsld.tfm
newtxtt/tfm/newtxbttsldq.tfm
newtxtt/tfm/newtxbttsle.tfm
newtxtt/tfm/newtxbttsleq.tfm
newtxtt/tfm/newtxbttza.tfm
newtxtt/tfm/newtxbttzaq.tfm
newtxtt/tfm/newtxbttzb.tfm
newtxtt/tfm/newtxbttzbq.tfm
newtxtt/tfm/newtxbttzc.tfm
newtxtt/tfm/newtxbttzcq.tfm
newtxtt/tfm/newtxbttzd.tfm
newtxtt/tfm/newtxbttzdq.tfm
newtxtt/tfm/newtxbttze.tfm
newtxtt/tfm/newtxbttzeq.tfm
newtxtt/tfm/newtxbttzsca.tfm
newtxtt/tfm/newtxbttzscaq.tfm
newtxtt/tfm/newtxbttzscb.tfm
newtxtt/tfm/newtxbttzscbq.tfm
newtxtt/tfm/newtxbttzscc.tfm
newtxtt/tfm/newtxbttzsccq.tfm
newtxtt/tfm/newtxbttzscd.tfm
newtxtt/tfm/newtxbttzscdq.tfm
newtxtt/tfm/newtxbttzsce.tfm
newtxtt/tfm/newtxbttzsceq.tfm
newtxtt/tfm/newtxbttzsla.tfm
newtxtt/tfm/newtxbttzslaq.tfm
newtxtt/tfm/newtxbttzslb.tfm
newtxtt/tfm/newtxbttzslbq.tfm
newtxtt/tfm/newtxbttzslc.tfm
newtxtt/tfm/newtxbttzslcq.tfm
newtxtt/tfm/newtxbttzsld.tfm
newtxtt/tfm/newtxbttzsldq.tfm
newtxtt/tfm/newtxbttzsle.tfm
newtxtt/tfm/newtxbttzsleq.tfm
newtxtt/tfm/newtxtta.tfm
newtxtt/tfm/newtxttaq.tfm
newtxtt/tfm/newtxttb.tfm
newtxtt/tfm/newtxttbq.tfm
newtxtt/tfm/newtxttc.tfm
newtxtt/tfm/newtxttcq.tfm
newtxtt/tfm/newtxttd.tfm
newtxtt/tfm/newtxttdq.tfm
newtxtt/tfm/newtxtte.tfm
newtxtt/tfm/newtxtteq.tfm
newtxtt/tfm/newtxttsca.tfm
newtxtt/tfm/newtxttscaq.tfm
newtxtt/tfm/newtxttscb.tfm
newtxtt/tfm/newtxttscbq.tfm
newtxtt/tfm/newtxttscc.tfm
newtxtt/tfm/newtxttsccq.tfm
newtxtt/tfm/newtxttscd.tfm
newtxtt/tfm/newtxttscdq.tfm
newtxtt/tfm/newtxttsce.tfm
newtxtt/tfm/newtxttsceq.tfm
newtxtt/tfm/newtxttsla.tfm
newtxtt/tfm/newtxttslaq.tfm
newtxtt/tfm/newtxttslb.tfm
newtxtt/tfm/newtxttslbq.tfm
newtxtt/tfm/newtxttslc.tfm
newtxtt/tfm/newtxttslcq.tfm
newtxtt/tfm/newtxttsld.tfm
newtxtt/tfm/newtxttsldq.tfm
newtxtt/tfm/newtxttsle.tfm
newtxtt/tfm/newtxttsleq.tfm
newtxtt/tfm/newtxttza.tfm
newtxtt/tfm/newtxttzaq.tfm
newtxtt/tfm/newtxttzb.tfm
newtxtt/tfm/newtxttzbq.tfm
newtxtt/tfm/newtxttzc.tfm
newtxtt/tfm/newtxttzcq.tfm
newtxtt/tfm/newtxttzd.tfm
newtxtt/tfm/newtxttzdq.tfm
newtxtt/tfm/newtxttze.tfm
newtxtt/tfm/newtxttzeq.tfm
newtxtt/tfm/newtxttzsca.tfm
newtxtt/tfm/newtxttzscaq.tfm
newtxtt/tfm/newtxttzscb.tfm
newtxtt/tfm/newtxttzscbq.tfm
newtxtt/tfm/newtxttzscc.tfm
newtxtt/tfm/newtxttzsccq.tfm
newtxtt/tfm/newtxttzscd.tfm
newtxtt/tfm/newtxttzscdq.tfm
newtxtt/tfm/newtxttzsce.tfm
newtxtt/tfm/newtxttzsceq.tfm
newtxtt/tfm/newtxttzsla.tfm
newtxtt/tfm/newtxttzslaq.tfm
newtxtt/tfm/newtxttzslb.tfm
newtxtt/tfm/newtxttzslbq.tfm
newtxtt/tfm/newtxttzslc.tfm
newtxtt/tfm/newtxttzslcq.tfm
newtxtt/tfm/newtxttzsld.tfm
newtxtt/tfm/newtxttzsldq.tfm
newtxtt/tfm/newtxttzsle.tfm
newtxtt/tfm/newtxttzsleq.tfm
newtxtt/type1/newtcxbtt.pfb
newtxtt/type1/newtcxtt.pfb
newtxtt/type1/newtxbtt.pfb
newtxtt/type1/newtxbttsc.pfb
newtxtt/type1/newtxtt.pfb
newtxtt/type1/newtxttsc.pfb
EOF
)

# Process ONLY the explicitly listed files.
while IFS= read -r file; do

    # Ignore empty lines.
    [[ -z "$file" ]] && continue

    # Skip nonexistent files.
    [[ -e "$file" || -L "$file" ]] || continue

    # Get the committer date of the last commit touching this file.
    # Format required by touch -t: YYYYMMDDhhmm.ss
    date=$(git log -1 --format=%cd \
        --date=format-local:%Y%m%d%H%M.%S HEAD -- "$file")

    # Skip files without Git history.
    [[ -z "$date" ]] && continue

    # Set BOTH access time (atime) and modification time (mtime).
    # -c: do not create nonexistent files
    # -h: affect symbolic links themselves, not their targets
    # -t: use the specified timestamp
    # File contents remain unchanged.
    touch -ch -t "$date" -- "$file"

    # Report the operation.
    printf 'OK: %s -> %s\n' "$file" "$date"

done <<< "$files"
