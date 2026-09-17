#!/usr/bin/env bash
set -euo pipefail

if [ "$EUID" -ne 0 ]; then
    echo "==> Error: install.sh must be run as root (use sudo ./install.sh)"
    exit 1
fi

THEME_NAME="mono-boot"
THEME_DIR="/usr/share/plymouth/themes/${THEME_NAME}"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================================"
echo " Installing Mono Boot Theme (Minimalist Monochrome)"
echo "============================================================"

echo "==> [1/5] Installing ${THEME_NAME} theme to ${THEME_DIR}..."
mkdir -p "${THEME_DIR}"
cp -f "${SOURCE_DIR}"/*.png "${THEME_DIR}/" 2>/dev/null || true
cp -f "${SOURCE_DIR}/mono-boot.plymouth" "${THEME_DIR}/"
cp -f "${SOURCE_DIR}/mono-boot.script" "${THEME_DIR}/"

if [ -d "${SOURCE_DIR}/donut_frames" ]; then
    mkdir -p "${THEME_DIR}/donut_frames"
    cp -rf "${SOURCE_DIR}/donut_frames"/* "${THEME_DIR}/donut_frames/"
fi

chmod -R 644 "${THEME_DIR}"/*
chmod 755 "${THEME_DIR}" "${THEME_DIR}/donut_frames" 2>/dev/null || true

echo "==> [2/5] Updating /etc/mkinitcpio.conf..."
# Ensure early KMS i915 driver is in MODULES
if grep -q 'MODULES=(i915)' /etc/mkinitcpio.conf && grep -q 'MODULES=(btrfs)' /etc/mkinitcpio.conf; then
    sed -i -E 's/^MODULES=\(btrfs\)/MODULES=(btrfs i915)/' /etc/mkinitcpio.conf
    sed -i -E '/^MODULES=\(i915\)/d' /etc/mkinitcpio.conf
elif ! grep -q -E '^MODULES=.*i915' /etc/mkinitcpio.conf; then
    sed -i -E 's/^MODULES=\(([^)]*)\)/MODULES=(\1 i915)/' /etc/mkinitcpio.conf
fi

# Ensure plymouth hook is present immediately after udev
if ! grep -q -E 'HOOKS=.*plymouth' /etc/mkinitcpio.conf; then
    sed -i -E 's/HOOKS=\((base udev|udev)/HOOKS=(\1 plymouth/' /etc/mkinitcpio.conf
fi

echo "Current mkinitcpio configuration:"
grep -E '^(MODULES|HOOKS)' /etc/mkinitcpio.conf

echo "==> [3/5] Setting default Plymouth theme to ${THEME_NAME}..."
plymouth-set-default-theme "${THEME_NAME}"

echo "==> [4/5] Regenerating initramfs with mkinitcpio -P..."
mkinitcpio -P

echo "==> [5/5] Verifying systemd-boot loader options..."
BOOT_ENTRY="/boot/loader/entries/2025-07-16_18-17-02_linux.conf"
if [ -f "${BOOT_ENTRY}" ]; then
    if ! grep -q 'quiet splash' "${BOOT_ENTRY}"; then
        sed -i 's/\(^options .*\)/\1 quiet splash loglevel=3 rd.udev.log_priority=3 vt.global_cursor_default=0/' "${BOOT_ENTRY}"
        echo "Updated ${BOOT_ENTRY}."
    else
        echo "${BOOT_ENTRY} contains quiet splash parameters."
    fi
    grep '^options' "${BOOT_ENTRY}"
fi

# Clean up obsolete rocket-split theme if present
if [ -d "/usr/share/plymouth/themes/rocket-split" ]; then
    echo "==> Removing obsolete rocket-split theme..."
    rm -rf "/usr/share/plymouth/themes/rocket-split"
fi

echo "============================================================"
echo " Installation complete! Mono Boot is now your default splash."
echo "============================================================"
