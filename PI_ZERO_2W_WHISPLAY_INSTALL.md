# Raspberry Pi Zero 2 W + Whisplay Install Guide

This guide walks through installing **Tamagotchi Pet** on a **Raspberry Pi Zero 2 W** using a **PiSugar battery board** and **PiSugar Whisplay HAT**.

The project currently runs as a Python/Pygame virtual pet and is intended for a small Raspberry Pi handheld build.

Repository:

```bash
git clone https://github.com/IndiaRubber/tamagotchi-pet.git
```

---

## Hardware used

Recommended build hardware:

- Raspberry Pi Zero 2 W
- MicroSD card, 16 GB or larger
- PiSugar battery board
- PiSugar Whisplay HAT
- Small speaker, if not already connected through the Whisplay setup
- USB power supply
- Optional: mini HDMI adapter, USB keyboard, or USB serial adapter for troubleshooting

---

## 1. Flash Raspberry Pi OS

Use **Raspberry Pi Imager** on your computer.

Recommended image:

```text
Raspberry Pi OS Lite, 32-bit
```

Before flashing, open the Imager settings and configure:

```text
Hostname: peta.local or petb.local
Username: sifting
Password: your password
Wi-Fi: your 2.4 GHz Wi-Fi network
SSH: enabled
```

The Raspberry Pi Zero 2 W only supports 2.4 GHz Wi-Fi, so make sure the network you configure is available on 2.4 GHz.

After flashing, insert the SD card into the Pi and boot it.

---

## 2. SSH into the Pi

From PowerShell, Windows Terminal, macOS Terminal, or Linux Terminal:

```bash
ssh sifting@peta.local
```

Or use the Pi's IP address:

```bash
ssh sifting@192.168.x.x
```

Update the system:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

Reconnect after reboot:

```bash
ssh sifting@peta.local
```

---

## 3. Install base packages

Install Git, Python tooling, Pygame dependencies, and bus diagnostic tools:

```bash
sudo apt install -y \
  git \
  python3 \
  python3-venv \
  python3-pip \
  python3-pygame \
  libsdl2-2.0-0 \
  libsdl2-image-2.0-0 \
  libsdl2-mixer-2.0-0 \
  libsdl2-ttf-2.0-0 \
  i2c-tools \
  python3-smbus \
  raspi-config
```

---

## 4. Enable I2C and SPI

Run Raspberry Pi configuration:

```bash
sudo raspi-config
```

Go to:

```text
Interface Options
```

Enable:

```text
I2C
SPI
```

Then reboot:

```bash
sudo reboot
```

After reboot, check the I2C bus:

```bash
i2cdetect -y 1
```

For the PiSugar board, look for the expected PiSugar I2C address. On this build, address `75` has been seen when the PiSugar board is seated and connected correctly.

If the address disappears, check the physical connection before troubleshooting software. Reseating the HAT or checking the battery wires may be required.

---

## 5. Install the Whisplay driver

Clone the official Whisplay driver repository:

```bash
cd ~
git clone https://github.com/PiSugar/Whisplay.git --depth 1
cd Whisplay
sudo bash install_driver.sh
sudo reboot
```

The Whisplay HAT uses I2C, SPI, and I2S buses. The official driver installer enables the required I2C and I2S audio pieces during installation.

After reboot, reconnect:

```bash
ssh sifting@peta.local
```

---

## 6. Test the Whisplay hardware

Run the Whisplay example test before installing the pet app:

```bash
cd ~/Whisplay/example
pip install -r requirements.txt --break-system-packages
bash run_test.sh
```

Confirm that these work:

```text
Screen displays the test output
Speaker/audio works
Button responds
LEDs respond
No major driver errors appear
```

Do not close the case yet. This is the hardware checkpoint.

---

## 7. Optional: install the Whisplay daemon

The Whisplay repository includes an optional `whisplay-daemon` service.

It can manage:

- LCD display
- Backlight
- RGB LED
- Button events
- App foreground switching
- Built-in Bluetooth, Wi-Fi, and volume pages

Install it with:

```bash
cd ~/Whisplay
sudo bash daemon/install_whisplay_daemon_service.sh
systemctl status whisplay-daemon.service --no-pager
```

View logs:

```bash
journalctl -u whisplay-daemon.service -f
```

For early Tamagotchi testing, it may be easier to skip the daemon at first. First prove that the Whisplay test script works, then prove that `main.py` works, then decide whether to integrate the daemon later.

---

## 8. Clone Tamagotchi Pet

Clone the project:

```bash
cd ~
git clone https://github.com/IndiaRubber/tamagotchi-pet.git
cd tamagotchi-pet
```

If the repo is already cloned:

```bash
cd ~/tamagotchi-pet
git pull
```

---

## 9. Create the Python virtual environment

Create a virtual environment that can still see the system-installed Raspberry Pi Pygame package:

```bash
cd ~/tamagotchi-pet
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install project requirements:

```bash
pip install -r requirements.txt
```

If `pip install -r requirements.txt` tries to reinstall Pygame and fails on the Pi, use the system package instead:

```bash
sudo apt install -y python3-pygame
```

Then verify Pygame:

```bash
python -c "import pygame; print(pygame.version.ver)"
```

---

## 10. Run the pet manually

From the project folder:

```bash
cd ~/tamagotchi-pet
source .venv/bin/activate
python main.py
```

If running over SSH and targeting the attached display, try:

```bash
DISPLAY=:0 python main.py
```

If Pygame cannot open a display, install a minimal desktop/display stack:

```bash
sudo apt install -y raspberrypi-ui-mods
sudo reboot
```

Then try again:

```bash
cd ~/tamagotchi-pet
source .venv/bin/activate
DISPLAY=:0 python main.py
```

---

## 11. Create a manual launch script

Create a startup script:

```bash
nano ~/start_pet.sh
```

Paste:

```bash
#!/bin/bash
cd /home/sifting/tamagotchi-pet
source .venv/bin/activate
python main.py
```

Save and exit, then make it executable:

```bash
chmod +x ~/start_pet.sh
```

Test it:

```bash
~/start_pet.sh
```

---

## 12. Optional: start the pet automatically on boot

Only do this after manual launch works.

Create a systemd service:

```bash
sudo nano /etc/systemd/system/tamagotchi.service
```

Paste:

```ini
[Unit]
Description=Tamagotchi Pet
After=multi-user.target

[Service]
User=sifting
WorkingDirectory=/home/sifting/tamagotchi-pet
Environment=DISPLAY=:0
ExecStart=/home/sifting/tamagotchi-pet/.venv/bin/python /home/sifting/tamagotchi-pet/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable tamagotchi.service
sudo systemctl start tamagotchi.service
```

Check status:

```bash
sudo systemctl status tamagotchi.service
```

View logs:

```bash
journalctl -u tamagotchi.service -f
```

Stop the service while testing manually:

```bash
sudo systemctl stop tamagotchi.service
```

---

## 13. Final pre-case checklist

Before closing the case, run all three checks:

```bash
i2cdetect -y 1
```

```bash
cd ~/Whisplay/example
bash run_test.sh
```

```bash
cd ~/tamagotchi-pet
source .venv/bin/activate
python main.py
```

Only close the case after:

```text
PiSugar is detected
Whisplay test passes
Tamagotchi Pet launches manually
Buttons/display/audio are behaving as expected
```

---

## Useful troubleshooting commands

Check Pi model:

```bash
cat /proc/device-tree/model
```

Check I2C devices:

```bash
i2cdetect -y 1
```

Check Python version:

```bash
python --version
```

Check Pygame:

```bash
python -c "import pygame; print(pygame.version.ver)"
```

Check Git status:

```bash
cd ~/tamagotchi-pet
git status
```

Pull latest code:

```bash
cd ~/tamagotchi-pet
git pull
```

Run manually:

```bash
cd ~/tamagotchi-pet
source .venv/bin/activate
python main.py
```

Check auto-start logs:

```bash
journalctl -u tamagotchi.service -f
```

---

## Suggested build order for additional pets

For a second pet build, use this order:

```text
1. Assemble Pi Zero 2 W + PiSugar + Whisplay loosely
2. Flash Raspberry Pi OS
3. SSH into the Pi
4. Update the system
5. Enable I2C and SPI
6. Confirm PiSugar appears with i2cdetect -y 1
7. Install Whisplay driver
8. Reboot
9. Run Whisplay test script
10. Clone tamagotchi-pet
11. Create the Python virtual environment
12. Run python main.py manually
13. Add auto-start only after manual launch works
14. Close the case
```

The key rule: do not close the case until both the Whisplay test script and the pet app run successfully.
