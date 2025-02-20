#!/bin/bash

bytes1=0
bytes2=0

# Get the name of the network interface
interfaceName=$(ip -o -4 route show to default | sort -nk 9 | awk 'NR==1 {print $5}')

interfaceSymbol=""

if [[ $interfaceName == w* ]] ; then
  interfaceSymbol=""
fi

output1=$(cat /proc/net/dev)
sleep 1
output2=$(cat /proc/net/dev)

bytes1=$(echo "$output1" | awk '/'${interfaceName}':/ {print $2}')
bytes2=$(echo "$output2" | awk '/'${interfaceName}':/ {print $2}')

speed=$((bytes2 - bytes1))

if (( speed < 1024 )); then
  echo "${interfaceSymbol} ${speed} B/s"
elif (( speed < 1048576 )); then
  speedK=$((speed / 1024))
  echo "${interfaceSymbol} ${speedK} KB/s"
else
  speedM=$((speed / 1048576))
  echo "${interfaceSymbol} ${speedM} MB/s"
fi