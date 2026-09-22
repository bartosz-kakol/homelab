# Link map

The following **hard links** are assumed:

- `~/misc/crater/config.yaml` → `/etc/crater/config.yaml`

# Setup

1. Update the *Crater* submodule and [Install *Crater*](https://github.com/bartosz-kakol/crater#installation)
   ```bash
   scripts/update_crater
   ```
2. [Install *Tailscale*](https://console.tailscale.com/admin/machines/new-linux)
3. Create copies of `.dist` files and fill out required details:
	- `~/.env.dist`
	- `~/data/dnsmasq/dnsmasq.dist.conf`
	- `~/data/silo/config/config.dist.yaml`
	- `~/data/silo/config/volumes.dist.yaml`
	- `~/data/zigbee2mqtt/data/configuration.dist.yaml`
4. Setup Mosquitto password (use the one you configured in `~/data/zigbee2mqtt/data/configuration.yaml`):
   ```bash
   scripts/set_mosquitto_password z2m
   ```
5. Add firewall rule for `dnsmasq` to work via *Tailscale* using `ufw`:
   ```bash
   sudo ufw allow in on tailscale0 to any port 53
   ```
6. Install `bluez` and activate the `bluetooth` service (required for Home Assistant)
   ```bash
   sudo apt install bluez
   sudo systemctl enable --now bluetooth
   ```

# Additional configuration

## Allow `crater` to access main home directory

```bash
setfacl -m u:crater:x $HOME
```

## Create a `storage` group (or any other group) and assign it

```bash
sudo groupadd storage
sudo usermod -aG storage $USER
```

## Allow `crater` to write to `docker-compose.yaml`

```bash
setfacl -m u:crater:rw $HOME/docker-compose.yaml
```

## Login to GitHub's Docker Image Registry

```bash
docker login ghcr.io -u <github username>
```

## Create mount point

```bash
sudo mkdir /mnt/<name>
sudo chown -R $USER:storage /mnt/<name>
```

And append this to `/etc/fstab`:
```
UUID=ABCD-1234  /mnt/<name>  <filesystem>  uid=1000,gid=1001,fmask=017,dmask=007,nofail  0  0
```

> Replace `gid` with the ID of the `storage` group.

## Make a directory immutable (helpful for protecting mount points)

```bash
sudo chattr +i <path>
```
