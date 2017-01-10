#!/bin/bash
set -euo pipefail
cd "$(dirname $0)"

# This script is a drop-in replacement for the swift-dispersion-report command,
# that replays the output captures from this directory when suitable
# command-line arguments are given.

if [ $# -eq 0 ]; then
    echo "cannot replay \"swift-dispersion-report\": I only have a capture for \"swift-dispersion-report -j\"" >&2
    exit 1
fi
for ARG in "$@"; do
    case "${ARG}" in
        -j|--dump-json)
            # that's okay
            ;;
        *)
            echo "cannot replay \"swift-dispersion-report $@\": I only have a capture for \"swift-dispersion-report -j\"" >&2
            exit 1
            ;;
    esac
done

cat dispersion_json
