#!/bin/bash
set -euo pipefail
cd "$(dirname $0)"

# This script is a drop-in replacement for the swift-recon command, that
# replays the output captures from this directory when suitable command-line
# arguments are given.

FILEPATH="recon"
VERBOSE=0

# parse args and derive fixture name; e.g. "swift-recon object --replication"
# comes from test/fixtures/recon_object_replication
for ARG in "$@"; do
    case "${ARG}" in
        -v|--verbose)
            VERBOSE=1
            ;;
        --*)
            FILEPATH="${FILEPATH}_${ARG#--}"
            ;;
        *)
            FILEPATH="${FILEPATH}_${ARG}"
            ;;
    esac
done

if [ ! -f "${FILEPATH}" ]; then
    echo "cannot replay \"swift-recon $@\": capture file \"test/fixtures/${FILEPATH}\" not found" >&2
    exit 1
fi

if [ "${VERBOSE}" -eq 1 ]; then
    cat "${FILEPATH}"
else
    grep -v '^->' "${FILEPATH}"
fi
