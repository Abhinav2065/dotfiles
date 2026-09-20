#!/usr/bin/env bash

# Handler for Hyprland Lid Switch events
# Triggered by:
#   switch:on:Lid Switch  -> ~/.config/hypr/scripts/lid-handler.sh close
#   switch:off:Lid Switch -> ~/.config/hypr/scripts/lid-handler.sh open

ACTION="${1:-close}"
STATE_FILE="${HOME}/.config/laptop-mode/state"

MODE="pc"
if [[ -f "$STATE_FILE" ]]; then
    MODE="$(cat "$STATE_FILE" | tr -d '[:space:]')"
fi

lock_screen() {
    if ! pidof hyprlock >/dev/null 2>&1; then
        hyprlock &
    fi
}

case "$ACTION" in
    close)
        if [[ "$MODE" == "server" ]]; then
            # Server Mode: Turn off display only, keep all processes and servers running 100%
            hyprctl dispatch dpms off
        else
            # PC Mode:
            # 1. Lock screen with hyprlock (the ctrl+L lock screen)
            lock_screen
            # 2. Wait briefly for hyprlock to establish its lock surface before suspend
            sleep 0.5
            # 3. Turn off screen
            hyprctl dispatch dpms off
            # 4. Suspend system (preserves all existing applications, windows, and session state)
            systemctl suspend
        fi
        ;;
    open)
        # Turn display back on
        hyprctl dispatch dpms on
        if [[ "$MODE" != "server" ]]; then
            # Ensure lock screen is active on resume in PC mode
            lock_screen
        fi
        ;;
    *)
        echo "Usage: $0 [close|open]"
        exit 1
        ;;
esac
