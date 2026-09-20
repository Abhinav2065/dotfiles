#!/usr/bin/env bash

# Laptop Mode Manager (PC Mode vs Server Mode)
# Used by Waybar custom module, Hyprland startup, and power menu.

CONFIG_DIR="${HOME}/.config/laptop-mode"
STATE_FILE="${CONFIG_DIR}/state"
PID_FILE="${CONFIG_DIR}/inhibitor.pid"

mkdir -p "$CONFIG_DIR"

get_current_mode() {
    if [[ -f "$STATE_FILE" ]]; then
        cat "$STATE_FILE" | tr -d '[:space:]'
    else
        echo "pc"
    fi
}

stop_inhibitor() {
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid="$(cat "$PID_FILE" 2>/dev/null)"
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
    fi
    pkill -f "systemd-inhibit.*LaptopMode" 2>/dev/null || true
    pkill -f "systemd-inhibit.*ServerMode" 2>/dev/null || true
    pkill -f "systemd-inhibit.*PCMode" 2>/dev/null || true
}

start_inhibitor() {
    local mode="$1"
    stop_inhibitor

    if [[ "$mode" == "server" ]]; then
        # Server Mode: Inhibit both lid-switch and idle so system never sleeps or dims
        setsid systemd-inhibit --what=handle-lid-switch:idle --who="LaptopMode-Server" --why="Server Mode active" sleep infinity >/dev/null 2>&1 &
        local pid=$!
        disown "$pid" 2>/dev/null || true
        echo "$pid" > "$PID_FILE"
    else
        # PC Mode: Inhibit lid-switch from logind so Hyprland's lid-handler.sh has exclusive control of the lid close action (locking hyprlock first, then suspending cleanly)
        setsid systemd-inhibit --what=handle-lid-switch --who="LaptopMode-PC" --why="PC Mode lid handler active" sleep infinity >/dev/null 2>&1 &
        local pid=$!
        disown "$pid" 2>/dev/null || true
        echo "$pid" > "$PID_FILE"
    fi
}

set_mode() {
    local target="$1"
    local silent="$2"

    if [[ "$target" == "server" ]]; then
        echo "server" > "$STATE_FILE"
        # Stop hypridle so screen does not dim or lock while open
        pkill -x hypridle 2>/dev/null || true
        # Restore display brightness and ensure screen is on
        brightnessctl -r 2>/dev/null || true
        hyprctl dispatch dpms on 2>/dev/null || true
        # Inhibit logind lid switch and idle
        start_inhibitor "server"
        if [[ "$silent" != "silent" ]]; then
            notify-send -u normal -i server-database "Laptop Mode" "Switched to Server Mode\n• Screen stays on 100% while open\n• Screen turns off on lid close (laptop keeps running)" 2>/dev/null || true
        fi
    else
        echo "pc" > "$STATE_FILE"
        # Inhibit logind lid-switch so lid-handler controls hyprlock + suspend cleanly
        start_inhibitor "pc"
        # Start hypridle if installed
        if command -v hypridle >/dev/null 2>&1; then
            if ! pgrep -x hypridle >/dev/null; then
                setsid hypridle >/dev/null 2>&1 &
                disown 2>/dev/null || true
            fi
        fi
        # Ensure display is on
        hyprctl dispatch dpms on 2>/dev/null || true
        if [[ "$silent" != "silent" ]]; then
            notify-send -u normal -i computer "Laptop Mode" "Switched to PC Mode\n• Screen dims after 1m, locks after 2m\n• Lid close locks screen & suspends (keeps session intact)" 2>/dev/null || true
        fi
    fi

    # Instantly refresh Waybar
    pkill -RTMIN+8 waybar 2>/dev/null || true
}

output_status_json() {
    local mode
    mode="$(get_current_mode)"
    if [[ "$mode" == "server" ]]; then
        cat <<EOF
{"text":"󰒋","alt":"server","tooltip":"Mode: Server Mode\\n• Lid Close: Screen off only (laptop keeps running)\\n• Lid Open: Screen stays on 100%\\n\\nClick to switch to PC Mode","class":"server"}
EOF
    else
        cat <<EOF
{"text":"󰌢","alt":"pc","tooltip":"Mode: PC Mode (Normal)\\n• Lid Close: Lock screen & Suspend (keeps session intact)\\n• Idle 1m: Dim screen to 10%\\n• Idle 2m: Lock & turn screen off\\n\\nClick to switch to Server Mode","class":"pc"}
EOF
    fi
}

case "${1:-status}" in
    status)
        output_status_json
        ;;
    toggle)
        CURRENT="$(get_current_mode)"
        if [[ "$CURRENT" == "server" ]]; then
            set_mode "pc"
        else
            set_mode "server"
        fi
        ;;
    set)
        set_mode "$2"
        ;;
    init)
        CURRENT="$(get_current_mode)"
        set_mode "$CURRENT" "silent"
        ;;
    *)
        echo "Usage: $0 [status|toggle|set pc|set server|init]"
        exit 1
        ;;
esac
