import subprocess

def shell(command):
    process = subprocess.Popen(['/bin/bash', '-c', command])
    process.wait()

# Install required Python core libs
shell("sudo apt-get update")
shell("sudo apt-get upgrade -y")
shell("sudo apt-get install -y vim git python3-pip")
shell("sudo apt-get install --upgrade python3-setuptools")
shell("sudo apt-get install -y python3.11-venv")

# Raspberry Pi Config
shell("sudo raspi-config nonint do_vnc 0") #Enable VNC

# For Valet Vision Only
shell("sudo raspi-config nonint do_spi 0") #Enable SPI
shell("sudo raspi-config nonint do_i2c 0") # Enable I2c
# Install libcamera libraries
shell("sudo apt-get install -y libcamera-v4l2 libcamera-tools libcamera-apps")

# Install OCR packages
shell("sudo apt install tesseract-ocr")

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
         git checkout dev""")

# Install usb_gadget
shell("cd /home/tapster/Projects/valet/zero-hid/usb_gadget; chmod +x installer.bash;")
shell("cd /home/tapster/Projects/valet/zero-hid/usb_gadget; sudo ./installer.bash;")

# Install zero-hid library
shell("""cd /home/tapster/Projects/valet;
         source env/bin/activate;
         python3 -m pip install ./zero-hid/;""")

# For Valet Vision Only
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

# For Valet Link Only:
# Required video capture settings
#shell("""echo "dtoverlay=tc358743" | sudo tee -a /boot/firmware/config.txt;
#         echo "dtoverlay=tc358743-audio" | sudo tee -a /boot/firmware/config.txt;""")

# For Valet Link Only:
# Required video capture settings
#shell("""sudo truncate -s-1 /boot/firmware/cmdline.txt;
#         echo -n " cma=96M" | sudo tee -a /boot/firmware/cmdline.txt;""")

# For Valet Link Only:
# Install Checkbox Server Service
#shell("""cd /home/tapster/Projects/valet/checkbox-server/service;
#         sudo cp checkbox-server-hdmi.service /etc/systemd/system/checkbox-server-hdmi.service;
#         sudo chmod 644 /etc/systemd/system/checkbox-server-hdmi.service;
#         sudo systemctl daemon-reload;
#         sudo systemctl start checkbox-server-hdmi;
#         sudo systemctl enable checkbox-server-hdmi;""")

# For Valet Vision Only:
# Install Checkbox Server Service
shell("""cd /home/tapster/Projects/valet/checkbox-server/service;
         sudo cp checkbox-server-camera.service /etc/systemd/system/checkbox-server-camera.service;
         sudo chmod 644 /etc/systemd/system/checkbox-server-camera.service;
         sudo systemctl daemon-reload;
         sudo systemctl start checkbox-server-camera;
         sudo systemctl enable checkbox-server-camera;""")


# Install Comitup
shell("""cd /home/tapster/Projects/valet/;
         mkdir comitup;
         cd comitup;
         wget https://davesteele.github.io/comitup/latest/davesteele-comitup-apt-source_latest.deb;
         sudo dpkg -i --force-all davesteele-comitup-apt-source_latest.deb;
         sudo apt-get update;
         sudo apt-get install -y comitup comitup-watch;""")

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

