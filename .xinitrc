#!/bin/bash

# Disable screen blanking and power saving mechanisms
xset s off
xset s noblank
xset -dpms

# Start the Openbox window manager in the background
openbox-session &

# Start the cursor parking script in the background
~/mouse-park.sh &

# Launch Chromium in fullscreen kiosk mode
exec chromium-browser \
  --kiosk \
  --disable-infobars \
  --disable-pinch \
  --overscroll-history-navigation=0 \
  --touch-events=enabled \
  --force-device-scale-factor=1.25 \
  "http://localhost:8123"
