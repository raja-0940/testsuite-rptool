#!/bin/sh
# Normalize git version to PEP 440 format
# Usage: ./get-version.sh

set -e

# Get version from git
GIT_VERSION=$(git describe --tags --always --dirty 2>/dev/null || echo "unknown")

# Normalize to PEP 440
case "$GIT_VERSION" in
    v*-*-g*-dirty)
        # v1.2.3-5-gabc123-dirty → 1.2.3.post5+gabc123.dirty
        echo "$GIT_VERSION" | sed -E 's/^v([0-9.]+)-([0-9]+)-g([0-9a-f]+)-dirty$/\1.post\2+g\3.dirty/'
        ;;
    v*-*-g*)
        # v1.2.3-5-gabc123 → 1.2.3.post5+gabc123
        echo "$GIT_VERSION" | sed -E 's/^v([0-9.]+)-([0-9]+)-g([0-9a-f]+)$/\1.post\2+g\3/'
        ;;
    v*-dirty)
        # v1.2.3-dirty → 1.2.3.dirty
        echo "$GIT_VERSION" | sed 's/^v//; s/-dirty$/.dirty/'
        ;;
    v*)
        # v1.2.3 → 1.2.3
        echo "$GIT_VERSION" | sed 's/^v//'
        ;;
    *-dirty)
        # abc123-dirty → 0.0.0+abc123.dirty
        echo "$GIT_VERSION" | sed 's/-dirty$/.dirty/; s/^/0.0.0+/'
        ;;
    unknown)
        echo "0.0.0+unknown"
        ;;
    *)
        # abc123 → 0.0.0+abc123
        echo "0.0.0+$GIT_VERSION"
        ;;
esac
