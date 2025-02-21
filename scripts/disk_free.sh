#!/bin/bash

# Get the available free space in 1K blocks for root partition
available_kb=$(df --output=avail / | tail -n 1)

# Convert the available space to gigabytes with one decimal place
available_gb=$(awk "BEGIN {printf \"%.1f\", $available_kb/1024/1024}")

echo "$available_gb"