#!/usr/bin/env bash
STAT_FILE="/dev/shm/hyprlock_cpu.stat"

# CPU %
read -r _ u n s i io ir st _ < /proc/stat
total=$((u + n + s + i + io + ir + st))
idle=$((i + io))
cpu_pct=0
if [ -f "$STAT_FILE" ]; then
    read -r p_total p_idle < "$STAT_FILE"
    d_total=$((total - p_total))
    d_idle=$((idle - p_idle))
    if [ $d_total -gt 0 ]; then
        cpu_pct=$(( (d_total - d_idle) * 100 / d_total ))
    fi
fi
echo "$total $idle" > "$STAT_FILE"

# CPU Temp
cpu_temp="--"
for n in /sys/class/hwmon/hwmon*/name; do
    if grep -q "coretemp" "$n" 2>/dev/null; then
        d=$(dirname "$n")
        if [ -f "$d/temp1_input" ]; then
            raw=$(cat "$d/temp1_input")
            cpu_temp="$((raw / 1000))°C"
            break
        fi
    fi
done

# Fan Speed
fan_rpm="--"
for f in /sys/class/hwmon/hwmon*/fan1_input; do
    if [ -f "$f" ]; then
        fan_rpm="$(cat "$f") RPM"
        break
    fi
done

# RAM
read -r _ mtotal _ < <(grep MemTotal /proc/meminfo)
read -r _ mavail _ < <(grep MemAvailable /proc/meminfo)
mused=$((mtotal - mavail))
ram_pct=$((mused * 100 / mtotal))
ram_used_gb=$(awk "BEGIN {printf \"%.1f\", $mused/1048576}")
ram_tot_gb=$(awk "BEGIN {printf \"%.1f\", $mtotal/1048576}")

# Battery
bat_pct="100"
bat_stat="AC"
if [ -f /sys/class/power_supply/BAT0/capacity ]; then
    bat_pct="$(cat /sys/class/power_supply/BAT0/capacity)"
    bat_stat="$(cat /sys/class/power_supply/BAT0/status)"
fi

make_bar() {
    local pct=$1 width=10
    [ "$pct" -gt 100 ] 2>/dev/null && pct=100
    [ "$pct" -lt 0 ] 2>/dev/null && pct=0
    local filled=$((pct * width / 100))
    local empty=$((width - filled))
    local b=""
    for ((k=0; k<filled; k++)); do b+="█"; done
    for ((k=0; k<empty; k++)); do b+="░"; done
    echo "$b"
}

# Zero-width space prefix to prevent trimming
printf "\xe2\x80\x8b"
printf "── HARDWARE STATUS ────────\n"
printf "CPU LOAD   [%s] %2d%%\n" "$(make_bar "$cpu_pct")" "$cpu_pct"
printf "CPU TEMP   %s\n" "$cpu_temp"
printf "\n"
printf "RAM USAGE  [%s] %2d%%\n" "$(make_bar "$ram_pct")" "$ram_pct"
printf "RAM USED   %s / %s GB\n" "$ram_used_gb" "$ram_tot_gb"
printf "\n"
printf "FAN SPEED  %s\n" "$fan_rpm"
printf "\n"
printf "BATTERY    [%s] %2d%%\n" "$(make_bar "$bat_pct")" "$bat_pct"
printf "STATUS     %s\n" "$bat_stat"
