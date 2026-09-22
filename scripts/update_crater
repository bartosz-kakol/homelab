#!/bin/bash
set -e
shopt -s nullglob

sudo echo "Authorized."

cd ~/crater

echo " -- Pulling changes from git"
git pull
echo

echo " -- Building frontend"
pnpm install
pnpm --filter frontend build
echo

echo " -- Building app"
rm dist/*.whl
uv build --wheel

whl_candidates=(dist/*.whl)

if [ "${#whl_candidates[@]}" -ne 1 ]; then
    echo "❓ Expected exactly one .whl in dist/, found ${#files[@]}" >&2
    exit 1
fi

whl_file=${whl_candidates[0]##*/}

echo "🛞 Got wheel named $whl_file"
echo

echo " -- Installing new version"
#sudo rm -f -- /home/crater/*.whl
sudo find /home/crater -maxdepth 1 -type f -name '*.whl' -delete
sudo cp dist/$whl_file /home/crater/

echo -n "Install dependencies too? (Y/n): "
read install_dependencies

if [[ $answer == [yY] ]]; then
	sudo -u crater /home/crater/venv/bin/pip install --force-reinstall /home/crater/$whl_file
else
	sudo -u crater /home/crater/venv/bin/pip install --force-reinstall --no-deps /home/crater/$whl_file
fi
echo

echo " -- Finish"
echo "All done!"
