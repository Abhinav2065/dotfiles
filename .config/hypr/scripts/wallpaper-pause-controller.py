#!/usr/bin/env python3
import os
import sys
import json
import time
import socket
import subprocess

SOCKET_IPC = "/tmp/mpvpaper.sock"

# Classes that have transparent backgrounds or shouldn't pause wallpaper
DEFAULT_TRANSPARENT_CLASSES = {
    "",                 # empty workspace / no focused window
    "kitty",
    "foot",
    "alacritty",
    "wezterm",
    "ghostty",
    "st",
    "st-256color",
    "cava",
    "glava",
}

# Allow user custom list from ~/.config/hypr/transparent_apps.txt if present
config_file = os.path.expanduser("~/.config/hypr/transparent_apps.txt")
if os.path.exists(config_file):
    try:
        with open(config_file) as f:
            for line in f:
                item = line.strip().lower()
                if item and not item.startswith("#"):
                    DEFAULT_TRANSPARENT_CLASSES.add(item)
    except Exception as e:
        print(f"Error reading {config_file}: {e}", file=sys.stderr)

def get_hyprland_socket():
    xdg_runtime = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    if not sig:
        hypr_dir = os.path.join(xdg_runtime, "hypr")
        if os.path.exists(hypr_dir):
            sigs = [d for d in os.listdir(hypr_dir) if os.path.isdir(os.path.join(hypr_dir, d))]
            if sigs:
                sig = sigs[0]
    if not sig:
        return None
    sock_path = os.path.join(xdg_runtime, "hypr", sig, ".socket2.sock")
    return sock_path if os.path.exists(sock_path) else None

def send_mpv_pause(pause: bool):
    if not os.path.exists(SOCKET_IPC):
        return False
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect(SOCKET_IPC)
        cmd = {"command": ["set_property", "pause", pause]}
        s.sendall(json.dumps(cmd).encode() + b"\n")
        s.recv(1024)
        s.close()
        return True
    except Exception:
        return False

def get_active_window_class():
    try:
        res = subprocess.run(["hyprctl", "activewindow", "-j"], capture_output=True, text=True, timeout=1)
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout)
            return data.get("class", "").lower()
    except Exception:
        pass
    return ""

def update_pause_state(active_class=None):
    if active_class is None:
        active_class = get_active_window_class()
    active_class = active_class.lower()

    # If active window is transparent (or empty workspace), resume playback
    # If active window is opaque (e.g. firefox, chrome, etc.), pause playback
    should_pause = (active_class not in DEFAULT_TRANSPARENT_CLASSES)
    send_mpv_pause(should_pause)

def main():
    for _ in range(10):
        if os.path.exists(SOCKET_IPC):
            break
        time.sleep(0.5)

    hypr_sock_path = get_hyprland_socket()
    if not hypr_sock_path:
        sys.exit(1)

    update_pause_state()

    while True:
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(hypr_sock_path)

            buffer = ""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                buffer += data.decode(errors="ignore")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    if line.startswith("activewindow>>"):
                        payload = line[len("activewindow>>"):]
                        parts = payload.split(",", 1)
                        win_class = parts[0].strip() if parts else ""
                        update_pause_state(win_class)

                    elif line.startswith("workspace>>") or line.startswith("workspacev2>>"):
                        update_pause_state()

                    elif line.startswith("closewindow>>") or line.startswith("openwindow>>"):
                        update_pause_state()

        except Exception:
            time.sleep(2)

if __name__ == "__main__":
    main()
