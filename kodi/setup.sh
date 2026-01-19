#!/bin/bash

if [ "$EUID" -ne 0 ]; then
	echo "Please run as root (use sudo)"
	exit
fi

set -e

# Get the actual user who called sudo
REAL_USER=${SUDO_USER:-$USER}
REAL_GROUP=$(id -gn $REAL_USER)

# Install Kodi
DEFAULT_KODI_BIN_PATH="/usr/lib/x86_64-linux-gnu/kodi/kodi.bin"

if ! command -v kodi-standalone >/dev/null 2>&1; then
	apt install software-properties-common
	add-apt-repository -y ppa:team-xbmc/ppa
	apt install kodi
	echo "------------------"
else
	echo "Kodi is already installed"
fi

KODI_BIN_PATH=${1:-$DEFAULT_KODI_BIN_PATH}

if [[ ! -f "$KODI_BIN_PATH" ]]; then
	echo "❌ kodi.bin does not exist at: $KODI_BIN_PATH"
	echo "Pass the correct path as an argument. Make sure Kodi is installed."
	exit 1
fi

# Add permissions
usermod -aG audio,video,input,render,tty $REAL_USER

# Setup service
HOME_DIR_PATH=$(getent passwd "$REAL_USER" | cut -d: -f6)

echo "Kodi found at $KODI_BIN_PATH"
echo "User: $REAL_USER | Group: $REAL_GROUP"

cat <<EOF > /etc/systemd/system/kodi.service
[Unit]
Description=Kodi Media Center
After=network-online.target

[Service]
User=$REAL_USER
Group=$REAL_GROUP
Type=simple

ExecStartPre=+$HOME_DIR_PATH/video_control/on
ExecStart=$KODI_BIN_PATH --windowing=gbm --standalone
ExecStop=+$HOME_DIR_PATH/video_control/soft_off delay
ExecStopPost=+$HOME_DIR_PATH/video_control/soft_off delay

Environment=KODI_AE_SINK=ALSA
Environment=DBUS_SESSION_BUS_ADDRESS=""

Restart=no
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=4
SendSIGHUP=no
#SendSIGTERM=no
RemainAfterExit=no
SuccessExitStatus=0 1 139 143

StandardInput=tty-force
TTYPath=/dev/tty1
TTYVHangup=no
TTYVTDisallocate=no
StandardOutput=journal
SupplementaryGroups=audio video input render tty

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF > /etc/systemd/system/blank-startup.service
[Unit]
Description=Blank video signal on startup
# Ensure this runs after the physical TTYs are initialized
After=getty.target
# This ensures it stays 'active' until the very end of the shutdown process
DefaultDependencies=no
Conflicts=shutdown.target
Before=shutdown.target

[Service]
Type=oneshot
User=root
Group=root

ExecStart=$HOME_DIR_PATH/video_control/soft_off
ExecStop=$HOME_DIR_PATH/video_control/on

# Remain 'active' so systemd doesn't try to run it again
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

echo "📝 Wrote systemd service files, reloading daemon..."
systemctl daemon-reload

systemctl enable blank-startup

echo "✅ Done!"
echo ""
echo "⚠️ Run visudo and add this line to the bottom:"
echo "$REAL_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop kodi.service"
echo "Then change the power menu quit action to Custom and set it to this expression:"
echo "System.Exec(\"sudo systemctl stop kodi\")"
