#!/bin/bash
/bin/bash /home/rstasta/.config/eww/scripts/refresh_steam_charts.sh
eww daemon
sleep 1
eww open system-monitor
eww open steam-panel
