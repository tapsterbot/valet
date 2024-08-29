import argparse
import subprocess

def shell(command):
    process = subprocess.Popen(['/bin/bash', '-c', command])
    process.wait()

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

# Install required Python core libs
shell("sudo apt-get update")
shell("sudo apt-get upgrade -y")
shell("sudo apt-get install -y expect git vim python3-pip")
shell("sudo apt-get install -y --upgrade python3-setuptools")
shell("sudo apt-get install -y python3-venv")

# Raspberry Pi Config
shell("sudo raspi-config nonint do_vnc 0") #Enable VNC

##########################################
# For Valet Vision Only
if args.vision:
    shell("sudo raspi-config nonint do_spi 0") #Enable SPI
    shell("sudo raspi-config nonint do_i2c 0") # Enable I2c
    # Install libcamera libraries
    shell("sudo apt-get install -y libcamera-v4l2 libcamera-tools libcamera-apps")
##########################################

# Install OCR packages
shell("sudo apt install -y tesseract-ocr")

# Create Python Virtual Environment
shell("cd /home/tapster/; mkdir -p Projects/valet")
shell("cd /home/tapster/Projects/valet; python -m venv env --system-site-packages")

# Install OpenCV for Python
shell("cd /home/tapster/Projects/valet; source env/bin/activate; python3 -m pip install opencv-contrib-python")

# Install Tesseract for Python
shell("cd /home/tapster/Projects/valet; source env/bin/activate; python3 -m pip install pytesseract")

# Checkout zero-hid library
shell("""cd /home/tapster/Projects/valet;
         source env/bin/activate;
         git clone https://github.com/tapsterbot/zero-hid.git;
         cd zero-hid;
         git checkout touch-support""")

# Install usb_gadget
shell("cd /home/tapster/Projects/valet/zero-hid/usb_gadget; chmod +x installer;")
shell("""cd /home/tapster/Projects/valet/zero-hid/usb_gadget;
         sudo expect -c 'spawn ./installer; expect "Do you want to reboot? (Y/n)"; send "n\n"; interact';""")

# Install zero-hid library
shell("""cd /home/tapster/Projects/valet;
         source env/bin/activate;
         python3 -m pip install ./zero-hid/;""")

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
    # Install Comitup
    shell("""cd /home/tapster/Projects/valet/;
             mkdir comitup;
             cd comitup;
             wget https://davesteele.github.io/comitup/deb/python3-networkmanager_2.2-3_all.deb;
             sudo dpkg -i --force-all python3-networkmanager*.deb;
             wget https://davesteele.github.io/comitup/deb/comitup_1.42-1_all.deb;
             sudo dpkg -i --force-all comitup_*.deb;
             sudo apt-get update;
             sudo apt-get install -y python3-cachetools;
             sudo apt-get install -y comitup;""")

    # Allow NetworkManager to manage the wifi interfaces
    shell("""mkdir -pv /home/tapster/.ciusafe/etc/network/interfaces;
             cp -rv /etc/network/interfaces /home/tapster/.ciusafe/etc/network/interfaces;
             sudo rm /etc/network/interfaces;""")

    # Rename or delete /etc/wpa_supplicant/wpa_supplicant.conf
    shell("""mkdir -pv /home/tapster/.ciusafe/etc/wpa_supplicant;
             sudo mv -v  /etc/wpa_supplicant/wpa_supplicant.conf /home/tapster/.ciusafe/etc/wpa_supplicant/;""")

    # The systemd.resolved service should be disabled and masked to avoid contention for providing DNS service.
    shell("""sudo systemctl mask dnsmasq.service;
             sudo systemctl mask systemd-resolved.service;
             sudo systemctl mask dhcpd.service;
             sudo systemctl mask dhcpcd.service;
             sudo systemctl mask wpa-supplicant.service;
             sudo systemctl enable NetworkManager.service;""")

    # Edit comitup access point name
    shell("""sudo sed -i '/^# ap_name: comitup-<nnn>/a ap_name: <hostname>' /etc/comitup.conf""")

shell("sudo reboot now")

