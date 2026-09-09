#!/usr/bin/env bash
STATUS_FILE="/dev/shm/hyprlock_player_status"

user="$USER"
host="$(cat /etc/hostname 2>/dev/null || hostname 2>/dev/null || echo "archlinux")"
uptime_str="$(uptime -p 2>/dev/null | sed "s/^up //" || echo "")"

p_status="$(playerctl status 2>/dev/null || echo "Stopped")"
p_title="$(playerctl metadata title 2>/dev/null || echo "")"
p_artist="$(playerctl metadata artist 2>/dev/null || echo "")"
p_pos="$(playerctl metadata --format "{{duration(position)}}" 2>/dev/null || echo "")"
p_len="$(playerctl metadata --format "{{duration(mpris:length)}}" 2>/dev/null || echo "")"

# Cache status for visualizer
echo "$p_status" > "$STATUS_FILE"

# Clean up long title/artist (truncate to 24 chars)
if [ ${#p_title} -gt 24 ]; then
    p_title="${p_title:0:22}.."
fi
if [ ${#p_artist} -gt 24 ]; then
    p_artist="${p_artist:0:22}.."
fi

icon="▶"
if [ "$p_status" = "Paused" ]; then
    icon="⏸"
elif [ "$p_status" != "Playing" ]; then
    icon="⏹"
fi

time_str=""
if [ -n "$p_pos" ] && [ -n "$p_len" ]; then
    time_str="[$p_pos / $p_len] "
fi

# Zero-width space prefix to prevent trimming
printf "\xe2\x80\x8b"
printf "── USER SESSION ───────────\n"
printf "%s @ %s\n" "$user" "$host"
printf "uptime: %s\n" "$uptime_str"
printf "\n"
printf "── NOW PLAYING ────────────\n"
if [ "$p_status" = "Playing" ] || [ "$p_status" = "Paused" ]; then
    printf "%s %s\n" "$icon" "${p_title:-Unknown Title}"
    [ -n "$p_artist" ] && printf "  %s\n" "$p_artist"
    printf "  %s%s\n" "$time_str" "$p_status"
else
    printf "⏹ No active media\n"
    printf "  system idle\n"
fi
printf "\n"
printf "── SPECTRUM ───────────────\n"
