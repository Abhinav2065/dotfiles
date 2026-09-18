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

case "$ACTION" in
    close)
        if [[ "$MODE" == "server" ]]; then
            # Server Mode: Turn screen off, laptop stays running 100%
            hyprctl dispatch dpms off
        else
            # PC Mode: Turn off screen, lock, and suspend
            hyprctl dispatch dpms off
            pidof hyprlock >/dev/null 2>&1 || hyprlock &
            systemctl suspend
        fi
        ;;
    open)
        # Turn display back on
        hyprctl dispatch dpms on
        ;;
    *)
        echo "Usage: $0 [close|open]"
        exit 1
        ;;
esac
