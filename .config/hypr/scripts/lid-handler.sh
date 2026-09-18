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
        # Always lock screen when lid closes
        lock_screen
        sleep 0.3

        if [[ "$MODE" == "server" ]]; then
            # Server Mode: Turn screen off, keep processes running 100%
            hyprctl dispatch dpms off
        else
            # PC Mode: Turn off screen and suspend
            hyprctl dispatch dpms off
            systemctl suspend
        fi
        ;;
    open)
        # Turn display back on
        hyprctl dispatch dpms on
        # Guarantee that opening the lid presents the lockscreen
        lock_screen
        ;;
    *)
        echo "Usage: $0 [close|open]"
        exit 1
        ;;
esac
