#!/usr/bin/env bash
set -euo pipefail

if [ "$EUID" -ne 0 ]; then
    echo "==> Error: test.sh must be run as root (use sudo ./test.sh)"
    exit 1
fi

THEME="mono-boot"
echo "==> Testing Plymouth theme '${THEME}' for 7 seconds..."

# Start plymouthd
plymouthd --debug --tty=/dev/tty2 --no-daemon &
PLYMOUTH_PID=$!
sleep 0.8

# Trigger splash
plymouth --show-splash
sleep 0.6

# Simulate progressive systemd boot status messages and progress percentages
plymouth --update="[  OK  ] Initializing systemd-udevd hardware daemon..."
plymouth --progress=0.15
sleep 0.5

plymouth --update="[  OK  ] Loading early KMS driver and virtual console..."
plymouth --progress=0.30
sleep 0.5

plymouth --update="[  OK  ] Mounting root and secondary filesystems (btrfs)..."
plymouth --progress=0.50
sleep 0.5

plymouth --update="[  OK  ] Reached target System Initialization..."
plymouth --progress=0.65
sleep 0.5

plymouth --update="[  OK  ] Starting NetworkManager.service..."
plymouth --progress=0.80
sleep 0.5

plymouth --update="[  OK  ] Starting Bluetooth and Audio subsystem..."
plymouth --progress=0.92
sleep 0.5

plymouth --update="[  OK  ] Starting Hyprland Wayland Compositor..."
plymouth --progress=1.00
sleep 1.5

plymouth quit
wait ${PLYMOUTH_PID} 2>/dev/null || true

echo "==> Test completed successfully."
