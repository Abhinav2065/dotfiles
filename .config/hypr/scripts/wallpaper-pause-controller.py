#!/usr/bin/env python3
import os
import sys
import json
import time
import socket
import subprocess

SOCKET_IPC = "/tmp/mpvpaper.sock"

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

def check_has_windows():
    # Check if the active workspace has any windows
    try:
        res = subprocess.run(["hyprctl", "activeworkspace", "-j"], capture_output=True, text=True, timeout=1)
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout)
            if data.get("windows", 0) > 0:
                return True
            return False
    except Exception:
        pass

    # Fallback: check if activewindow exists
    try:
        res2 = subprocess.run(["hyprctl", "activewindow", "-j"], capture_output=True, text=True, timeout=1)
        if res2.returncode == 0 and res2.stdout.strip():
            data2 = json.loads(res2.stdout)
            return bool(data2.get("class"))
    except Exception:
        pass
    return False

def update_pause_state():
    has_windows = check_has_windows()
    # If there is any app/window on the workspace, pause the video.
    # If the workspace is empty, play the video.
    send_mpv_pause(has_windows)

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

                    # Trigger on any window or workspace changes
                    if any(line.startswith(prefix) for prefix in (
                        "workspace>>", "workspacev2>>",
                        "activewindow>>", "activewindowv2>>",
                        "openwindow>>", "closewindow>>",
                        "movewindow>>", "movewindowv2>>",
                        "focusedmon>>"
                    )):
                        update_pause_state()

        except Exception:
            time.sleep(2)

if __name__ == "__main__":
    main()
