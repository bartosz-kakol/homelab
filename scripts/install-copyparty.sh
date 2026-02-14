#!/bin/bash

set -e
sudo apt install --no-install-recommends python3-pil ffmpeg
sudo wget https://github.com/9001/copyparty/releases/latest/download/copyparty-sfx.py -O /usr/local/bin/copyparty-sfx.py
set +e

sudo useradd -r -s /sbin/nologin -m -d /var/lib/copyparty copyparty
echo "% copyparty.d" | sudo tee /etc/copyparty.conf > /dev/null
#sudo ln -s $HOME/copyparty/ /etc/copyparty.d
sudo mkdir -p /etc/copyparty.d
for file in $HOME/copyparty/*.conf; do
	if [ -f "$file" ]; then
		abs_path=$(realpath "$file")
		filename=$(basename "$file")
		target_path="/etc/copyparty.d/$filename"
		echo "Link: $abs_path -> $target_path"
		sudo ln $abs_path $target_path
	fi
done

sleep 1

COPYPARTY_GROUP_GID=$(getent group copyparty | cut -d: -f3)

echo "copyparty groups has been assigned this GID: $COPYPARTY_GROUP_GID"
echo "use it in /etc/fstab for proper mounting permissions"
