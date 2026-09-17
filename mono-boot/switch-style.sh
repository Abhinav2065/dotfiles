#!/usr/bin/env bash
set -euo pipefail

STYLE="${1:-}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$STYLE" = "donut" ]; then
    echo "==> Switching mono-boot style to: 3D ASCII Donut (Hyprlock match)..."
    cp -f "${DIR}/mono-boot.script.donut" "${DIR}/mono-boot.script"
elif [ "$STYLE" = "arch" ]; then
    echo "==> Switching mono-boot style to: Arch Linux Silhouette (Minimalist)..."
    git checkout "${DIR}/mono-boot.script" 2>/dev/null || true
    # If not git tracked yet, keep the arch version
    if [ ! -f "${DIR}/mono-boot.script.arch" ]; then
        cp -f "${DIR}/mono-boot.script" "${DIR}/mono-boot.script.arch"
    else
        cp -f "${DIR}/mono-boot.script.arch" "${DIR}/mono-boot.script"
    fi
else
    echo "Usage: $0 [arch|donut]"
    echo "  arch  - Minimal Arch Linux silhouette logo with breathing opacity"
    echo "  donut - 3D rotating ASCII Donut matching your Hyprlock screen"
    exit 1
fi

echo "==> Style active in local repository: ${STYLE}"
echo "==> To apply to the system, run: sudo ./install.sh"
