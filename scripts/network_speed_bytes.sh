#!/bin/bash

# Determine the network interface
interfaceName=$(ip -o -4 route show to default | sort -nk 9 | awk 'NR==1 {print $5}')

# Get the current byte count
bytes1=$(cat /proc/net/dev | awk '/'${interfaceName}':/ {print $2}')

# Wait for 1 second
sleep 1

# Get the new byte count
bytes2=$(cat /proc/net/dev | awk '/'${interfaceName}':/ {print $2}')

# Calculate and output the difference
echo $((bytes2 - bytes1))