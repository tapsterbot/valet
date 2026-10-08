import argparse
import subprocess

failures = []

def shell(command):
    process = subprocess.Popen(['/bin/bash', '-c', command])
    process.wait()
    # Note: for multi-line commands, this is the exit code of the last command
    if process.returncode != 0:
        print(f"\n*** WARNING: Command failed (exit code {process.returncode}):\n{command}\n")
        failures.append((process.returncode, command))

def parse_arguments():
    parser = argparse.ArgumentParser(description='Tapster Valet - Machine Setup')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-v', '--vision', action='store_true', dest='vision',
        help='Setup for Valet Vision')
    group.add_argument('-l', '--link', action='store_true', dest='link',
        help='Setup for Valet Link')
    parser.add_argument('-n', '--nohotspot', action='store_true', dest='nohotspot',
        default = False,
        help='Use this option if you do *not* want to configure Valet as a Wi-Fi hotspot on first boot')
    parser.add_argument('--noreboot', action='store_true', dest='noreboot',
        default = False,
        help='Use this option if you do *not* want to reboot when set-up is finished')
    arguments = parser.parse_args()
    return arguments

args = parse_arguments()

print("\nTapster - Machine Setup\n=======================")
if args.vision:
    print("Product: Valet Vision")

if args.link:
    print("Product: Valet Link")

if args.nohotspot:
    print("Hotspot: False")
else:
    print("Hotspot: True")

print()

# Install required packages
shell("sudo apt-get update")
shell("sudo apt-get upgrade -y")
shell("sudo apt-get install -y expect git vim python3-pip python3-dev build-essential")
shell("sudo apt-get install -y --upgrade python3-setuptools")
shell("sudo apt-get install -y python3-venv python3-pil python3-numpy")
shell("sudo apt install -y dnsmasq iptables")

# Raspberry Pi Config
shell("sudo raspi-config nonint do_vnc 0") #Enable VNC

##########################################
# For Valet Vision Only
if args.vision:
    shell("sudo raspi-config nonint do_spi 0") #Enable SPI
    shell("sudo raspi-config nonint do_i2c 0") # Enable I2c
    # Install libcamera libraries
    shell("sudo apt-get install -y libcamera-v4l2 libcamera-tools rpicam-apps")
    # Install Picamera2 library
    shell("sudo apt-get install -y python3-picamera2")
    # For Checkbox Display Server
    shell("sudo apt install -y fonts-dejavu")
    shell("sudo apt install -y i2c-tools libgpiod-dev python3-libgpiod")

##########################################

# Install OCR packages
shell("sudo apt install -y tesseract-ocr")

# Create Python Virtual Environment
shell("cd /home/tapster/; mkdir -p Projects/valet")
shell("cd /home/tapster/Projects/valet; python -m venv env --system-site-packages")

# Install OpenCV for Python
shell("sudo apt install -y python3-opencv opencv-data")

# Install Tesseract for Python
shell("cd /home/tapster/Projects/valet; source env/bin/activate; python3 -m pip install pytesseract")

# Configuration for USB Ethernet gadget
# Add usb0 interface /etc/dnsmasq.d/usb0
cmd = 'echo """' + \
      'interface=usb0       # Use interface usb0\n' + \
      'listen-address=192.168.42.42   # Specify the address to listen on\n' + \
      'bind-dynamic         # Bind to the interface\n' + \
      'server=8.8.8.8       # Use Google DNS\n' + \
      'domain-needed        # Don\'t forward short names\n' + \
      'bogus-priv           # Drop the non-routed address spaces\n' + \
      'dhcp-range=192.168.42.50,192.168.42.60,12h\n' + \
      'dhcp-option=option:router,192.168.42.42\n' + \
      'dhcp-option=option:dns-server,8.8.8.8' + \
      '"""' + \
      ' | sudo tee /etc/dnsmasq.d/usb0'
shell(cmd)

# Add usb0 interface to network interfaces file
shell("mkdir -p /etc/network/interfaces.d")
cmd = 'echo """' + \
      'auto usb0\n' + \
      'allow-hotplug usb0\n' + \
      'iface usb0 inet static\n' + \
      '  address 192.168.42.42\n' + \
      '  netmask 255.255.255.0' + \
      '"""' + \
      ' | sudo tee /etc/network/interfaces.d/usb0'
shell(cmd)

# Enable IP forwarding
cmd = 'echo net.ipv4.ip_forward=1 | sudo tee /etc/sysctl.d/routing.conf'
shell(cmd)

# Checkout zero-hid library
# Re-add rc.local because it was removed in latest RPi OS. :/ TODO: Move away from rc.local?
shell("sudo touch /etc/rc.local")
shell("sudo chmod 755 /etc/rc.local")
shell("""echo -e '#!/bin/sh -e\nexit 0' | sudo tee -a /etc/rc.local""")

shell("""cd /home/tapster/Projects/valet;
         source env/bin/activate;
         git clone https://github.com/tapsterbot/zero-hid.git;
         cd zero-hid;
         git checkout touch-support""")

# Install usb_gadget
shell("cd /home/tapster/Projects/valet/zero-hid/usb_gadget; chmod +x installer;")
shell("""cd /home/tapster/Projects/valet/zero-hid/usb_gadget;
         sudo expect -c 'spawn ./installer; expect "Do you want to reboot? (Y/n)"; send "n\n"; interact';""")

# Set firewall forwarding & NAT rules
cmd = "sudo sed -i '/^\\/usr\\/bin\\/init_usb_gadget/i \\\n" + \
      'iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE\\' + \
      "' /etc/rc.local"
shell(cmd)

# Restart dnsmasq after loading USB gadget
cmd = "sudo sed -i '/^exit 0/i service dnsmasq restart' /etc/rc.local"
shell(cmd)

# Install zero-hid library
shell("""cd /home/tapster/Projects/valet;
         source env/bin/activate;
         python3 -m pip install ./zero-hid/;""")



# For Push Button Module (PBM) Dynamixel-powered side-button support:
## Enable serial connection hardware
shell("sudo raspi-config nonint do_serial_hw 0")
## Disable shell on serial connection
shell("sudo raspi-config nonint do_serial_cons 1")

## For Raspberry Pi 4, set UART0 (aka PL011, aka "/dev/ttyAMA0") as primary UART
# (Other Pi versions untested, and might be different)
# More info: https://www.raspberrypi.com/documentation/computers/configuration.html#configure-uarts
shell("""echo "dtoverlay=disable-bt" | sudo tee -a /boot/firmware/config.txt""")
shell("sudo systemctl disable hciuart")

## Install required libs:
shell("""cd /home/tapster/Projects/valet; 
         source env/bin/activate; 
         python3 -m pip install pyserial lgpio gpiozero;""")

# Install DynamixelSDK
shell("""cd /home/tapster/Projects/valet;
         source env/bin/activate; 
         git clone https://github.com/ROBOTIS-GIT/DynamixelSDK.git;
         python3 -m pip install ./DynamixelSDK/python/;""")

##########################################
# For Valet Vision Only
if args.vision:
    # Install Adafruit libraries
    shell("""cd /home/tapster/Projects/valet;
             source env/bin/activate;
             python3 -m pip install --upgrade adafruit-python-shell;
             python3 -m pip install adafruit-circuitpython-rgb-display;""")

    shell("""cd /home/tapster/Projects/valet;
             source env/bin/activate;
             wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py;
             echo "n" | sudo -E env PATH=$PATH python3 raspi-blinka.py;""")

    # Install Tapster LCD display test script
    shell("""cd /home/tapster/Projects/valet;
             git clone https://gist.github.com/hugs/559aa69d8870630bda790e77847f9847 setup-test;""")

    # For Checkbox Display Server
    shell("""cd /home/tapster/Projects/valet;
             source env/bin/activate;
             git clone https://github.com/tapsterbot/checkbox-display-server.git;
             cd checkbox-display-server;
             python3 -m pip install --upgrade --force-reinstall spidev;
             python3 -m pip install --upgrade -r requirements.txt;""")

    # Install Checkbox Display Server Service
    shell("""cd /home/tapster/Projects/valet/checkbox-display-server/service;
             sudo cp checkbox-display-server.service /etc/systemd/system/checkbox-display-server.service;
             sudo chmod 644 /etc/systemd/system/checkbox-display-server.service;
             sudo systemctl daemon-reload;
             sudo systemctl start checkbox-display-server;
             sudo systemctl enable checkbox-display-server;""")

##########################################

# Install Checkbox server
shell("""cd /home/tapster/Projects/valet;
         source env/bin/activate;
         git clone https://github.com/tapsterbot/checkbox-server.git;
         cd checkbox-server;
         python3 -m pip install -r requirements.txt;""")

# Install Checkbox client
shell("""cd /home/tapster/Projects/valet;
         source env/bin/activate;
         git clone https://github.com/tapsterbot/checkbox-client-python.git;
         cd checkbox-client-python;
         python3 -m pip install -r requirements.txt;""")

##########################################
# For Valet Link Only:
if args.link:
    # Install v4l2-ctl (used by Checkbox server to set up HDMI capture)
    shell("sudo apt-get install -y v4l-utils")

    # Required video capture settings
    shell("""echo "dtoverlay=tc358743" | sudo tee -a /boot/firmware/config.txt;
             echo "dtoverlay=tc358743-audio" | sudo tee -a /boot/firmware/config.txt;""")


    # Required video capture settings
    shell("""sudo truncate -s-1 /boot/firmware/cmdline.txt;
             echo -n " cma=96M" | sudo tee -a /boot/firmware/cmdline.txt;""")

    # Install Checkbox Server Service
    shell("""cd /home/tapster/Projects/valet/checkbox-server/service;
             sudo cp checkbox-server-hdmi.service /etc/systemd/system/checkbox-server-hdmi.service;
             sudo chmod 644 /etc/systemd/system/checkbox-server-hdmi.service;
             sudo systemctl daemon-reload;
             sudo systemctl start checkbox-server-hdmi;
             sudo systemctl enable checkbox-server-hdmi;""")
##########################################

##########################################
# For Valet Vision Only:
if args.vision:
    # Install Checkbox Server Service
    shell("""cd /home/tapster/Projects/valet/checkbox-server/service;
             sudo cp checkbox-server-camera.service /etc/systemd/system/checkbox-server-camera.service;
             sudo chmod 644 /etc/systemd/system/checkbox-server-camera.service;
             sudo systemctl daemon-reload;
             sudo systemctl start checkbox-server-camera;
             sudo systemctl enable checkbox-server-camera;""")
##########################################

# Make Valet a Wi-Fi hotspot on first boot, *unless* we explicitly say no.
if args.nohotspot:
    pass
else:
    # Set Wi-Fi country code. #TODO: Make this a command-line flag and/or optional
    shell("sudo raspi-config nonint do_wifi_country US")
    
    # Install Comitup from its apt repo, so updates arrive with apt upgrade
    # More info: https://davesteele.github.io/comitup/ppa.html
    shell("""cd /home/tapster/Projects/valet/;
             mkdir -p comitup;
             cd comitup;
             wget https://davesteele.github.io/comitup/deb/davesteele-comitup-apt-source_1.3_all.deb;
             sudo dpkg -i davesteele-comitup-apt-source_1.3_all.deb;
             sudo apt-get update;
             sudo apt-get install -y comitup;""")

    # The systemd.resolved service should be disabled and masked to avoid contention for providing DNS service.
    # (Do not mask wpa_supplicant.service: NetworkManager and Comitup need it for Wi-Fi.)
    shell("""sudo systemctl mask dnsmasq.service;
             sudo systemctl mask systemd-resolved.service;
             sudo systemctl enable NetworkManager.service;""")

    # Edit comitup access point name
    shell("""sudo sed -i '/^# ap_name: comitup-<nnn>/a ap_name: <hostname>' /etc/comitup.conf""")

# Summarize any failed commands
if failures:
    print(f"\n*** {len(failures)} command(s) failed during set-up:\n")
    for returncode, command in failures:
        print(f"[exit code {returncode}]\n{command}\n")
else:
    print("\nSet-up finished with no failed commands.\n")

if args.noreboot:
    print("Skipping reboot (--noreboot). Reboot when ready: sudo reboot")
else:
    shell("sudo reboot")

