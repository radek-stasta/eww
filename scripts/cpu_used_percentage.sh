#!/bin/bash

# Function to calculate CPU load
calculate_cpu_load() {
    # Read the first line from /proc/stat (which starts with 'cpu')
    cpu_line=$(head -n 1 /proc/stat)

    # Get the sum of all the CPU time fields (user, nice, system, idle, etc.)
    cpu_values=($cpu_line)
    total_time=0
    idle_time=${cpu_values[4]}  # idle time is the 5th value

    for value in "${cpu_values[@]:1}"; do
        total_time=$((total_time + value))
    done

    echo "$total_time $idle_time"
}

# Get the first set of values
read -r total1 idle1 < <(calculate_cpu_load)

# Wait for a short period (e.g., 1 second)
sleep 1

# Get the second set of values
read -r total2 idle2 < <(calculate_cpu_load)

# Calculate the difference in total and idle time
total_diff=$((total2 - total1))
idle_diff=$((idle2 - idle1))

# Calculate the CPU usage as a percentage
cpu_usage=$((100 * (total_diff - idle_diff) / total_diff))

echo $cpu_usage