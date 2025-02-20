#!/bin/bash
# Get the available free space in 1K blocks for /dev/disk/by-label/fedora
available_kb=$(df --output=avail /dev/disk/by-label/fedora | tail -n 1)

# Get total disk space in 1K blocks for /dev/disk/by-label/fedora
total_kb=$(df --output=size /dev/disk/by-label/fedora | tail -n 1)

# Calculate used space
used_kb=$(expr $total_kb - $available_kb)

# Calculate percentage of used space with two decimal places
percentage_used=$(awk "BEGIN {printf \"%.2f\", $used_kb/$total_kb*100}")
echo $percentage_used