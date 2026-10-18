# Home Lab

## Link map

The following **hard links** are assumed:

- `~/misc/crater/config.yaml` → `/etc/crater/config.yaml`
- `~/misc/fanc/fanc.yaml` → `/etc/fanc.yaml`

## Setup

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
4. Setup Mosquitto password (use the one you configured in `~/data/zigbee2mqtt/data/configuration.yaml`)
   ```bash
   scripts/set_mosquitto_password z2m
   ```
5. Add firewall rule for `dnsmasq` to work via *Tailscale* using `ufw`
   ```bash
   sudo ufw allow in on tailscale0 to any port 53
   ```
6. Install `bluez` and activate the `bluetooth` service (required for Home Assistant)
   ```bash
   sudo apt install bluez
   sudo systemctl enable --now bluetooth
   ```
7. Install and configure `cups`
	1. Install
	   ```bash
	   sudo apt install cups
	   ```
	2. Add yourself to the `lpadmin` group
	   ```bash
	   sudo usermod -aG lpadmin $USER
	   ```
	3. Edit `/etc/cups/cupsd.conf`:
		1. Comment out or change:
		   ```conf
		   # Listen localhost:631
		   Port 631
		   ```
		2. Allow remote access to the web interface - find the `<Location />` block and adjust:
		   ```conf
		   <Location />
		     Order allow,deny
		     Allow all
		   </Location>

		   <Location /admin>
		     Order allow,deny
		     Allow all
		   </Location>

		   <Location /admin/conf>
		     AuthType Default
		     Require user @SYSTEM
		     Order allow,deny
		     Allow all
		   </Location>
		   ```
		3. Enable sharing of the printer list to allow browsing from other machines:
		   ```conf
		   Browsing On
		   BrowseLocalProtocols dnssd
		   ```
		4. Enable printer sharing:
		   ```conf
		   DefaultShared Yes
		   ```
	4. Install **SpliX Extras**:
	   ```bash
	   sudo apt install printer-driver-splix
	   ```
	5. Restart `cups`:
	   ```bash
	   sudo systemctl restart cups
	   sudo systemctl enable cups
	   ```
8. Setup `fanc` for quiet work
	1. Install `smartmontools` and `hdparm`:
	   ```bash
	   sudo apt install smartmontools hdparm
	   ```
	2. Make the `drivetemp` kernel module auto-load (and load it manually):
	   ```bash
	   echo drivetemp | sudo tee /etc/modules-load.d/drivetemp.conf
	   sudo modprobe drivetemp
	   ```
	3. **May be important:** Modify the config at `~/misc/fanc/fanc.yaml` depending on what components are installed.
	4. Get the `fanc` binary and put it at `/usr/local/bin/fanc`:
	   ```bash
	   sudo install -m 755 fanc /usr/local/bin/fanc
	   ```
	5. Setup the `fanc` systemd service:
	   ```bash
	   sudo install -m 644 ~/misc/fanc/fanc.service /etc/systemd/system/fanc.service
	   sudo systemctl daemon-reload
	   sudo systemctl enable --now fanc
	   ```
9. Setup HDD drive spindown time for quiet work
	1. Identify the drive (match the drive IDs):
	   ```bash
	   sudo fdisk -l
	   ls /dev/disk/by-id/
	   ```
	2. Setup `/etc/hdparm.conf` (`127` is least aggressive power saving, `241` is 30 minutes):
	   ```conf
	   /dev/disk/by-id/ata-YOUR_DRIVE {
	       apm = 127
	       spindown_time = 241
	   }
	   ```
	3. **`hdparm` MAY NOT WORK with select drives!** `hd-idle` ca be the fix in some cases:
		1. Install `hd-idle`:
		   ```bash
		   sudo apt install hd-idle
		   ```
		2. Configure `hd-idle` by editing `/etc/default/hd-idle` (`1800` is 30 minutes in seconds):
		   ```env
		   START_HD_IDLE=true
		   HD_IDLE_OPTS="-i 0 -a /dev/disk/by-id/ata-YOUR_DRIVE -i 1800 -c ata"
		   ```
		3. For more drives, add a pair of `-a` and `-i` flags just before `-c ata`:
		   ```env
		   HD_IDLE_OPTS="-i 0 -a <drive_1_here> -i 1800 -a <drive_2_here> -i 1800 -c ata
		   ```

## Additional configuration

### Allow `crater` to access main home directory

```bash
setfacl -m u:crater:x $HOME
```

### Create a `storage` group (or any other group) and assign it

```bash
sudo groupadd storage
sudo usermod -aG storage $USER
```

### Allow `crater` to write to `docker-compose.yaml`

```bash
setfacl -m u:crater:rw $HOME/docker-compose.yaml
```

### Login to GitHub's Docker Image Registry

```bash
docker login ghcr.io -u <github username>
```

### Create mount point

```bash
sudo mkdir /mnt/<name>
sudo chown -R $USER:storage /mnt/<name>
```

And append this to `/etc/fstab`:
```
UUID=ABCD-1234  /mnt/<name>  <filesystem>  uid=1000,gid=1001,fmask=017,dmask=007,nofail  0  0
```

> Replace `gid` with the ID of the `storage` group.

### Make a directory immutable (helpful for protecting mount points)

```bash
sudo chattr +i <path>
```
