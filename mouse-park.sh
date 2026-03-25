#!/bin/bash

# Time in milliseconds to wait after a touch before moving the cursor
IDLE_LIMIT=500 
MOVED=0

while true; do
    # Get current idle time in milliseconds
    IDLE=$(xprintidle)

    if [ "$IDLE" -ge "$IDLE_LIMIT" ]; then
        if [ "$MOVED" -eq 0 ]; then
            # Teleport the cursor to the bottom right corner
            xdotool mousemove 9999 9999
            MOVED=1
        fi
        # Check less frequently when already idle to save CPU
        sleep 0.5
    else
        # Reset the moved flag and check frequently while active
        MOVED=0
        sleep 0.1
    fi
done
