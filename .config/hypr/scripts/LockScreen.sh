#!/usr/bin/env bash
pidof hyprlock >/dev/null 2>&1 || hyprlock &
