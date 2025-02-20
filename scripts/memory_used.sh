#!/bin/bash
free -m | awk '/^Mem:/ { printf("%.2f\n", $3 / 1024) }'