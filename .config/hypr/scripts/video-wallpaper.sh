#!/usr/bin/env bash

# Kill any existing instances
pkill -f wallpaper-pause-controller 2>/dev/null
pkill -x mpvpaper 2>/dev/null
pkill -x swww-daemon 2>/dev/null
rm -f /tmp/mpvpaper.sock

WALLPAPER="${1:-$HOME/.config/hypr/wallpapers/mandelbrot_infinite_loop_white.mp4}"

if [ ! -f "$WALLPAPER" ]; then
    WALLPAPER="$HOME/Downloads/mandelbrot_infinite_loop_white(1).mp4"
fi

# Start mpvpaper with IPC socket enabled and panscan=1.0 to fill screen without black bars
/home/ablag/.local/bin/mpvpaper -o "no-audio loop hwdec=auto panscan=1.0 input-ipc-server=/tmp/mpvpaper.sock" '*' "$WALLPAPER" &
MPV_PID=$!

# Start pause controller
python3 /home/ablag/.config/hypr/scripts/wallpaper-pause-controller.py &
CTRL_PID=$!

# Wait for mpvpaper; if it exits, clean up controller
wait $MPV_PID
kill $CTRL_PID 2>/dev/null
