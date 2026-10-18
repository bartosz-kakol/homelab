The `it87` module enables additional sensors on Gigabyte motheboards:

```bash
sudo apt install dkms build-essential git linux-headers-$(uname -r)
git clone https://github.com/frankcrawford/it87
cd it87
sudo make dkms
sudo modprobe it87
```

After verifying using the `sensors` command from `lm-sensors`, it can be set to auto-load:

```bash
echo it87 | sudo tee /etc/modules-load.d/it87.conf
```
