#!/usr/bin/env bash
if [ $(pwd) = "/home/pi/WeLAB-4-makers" ]; then
    sudo apt-get update && sudo apt-get upgrade -y
    sudo apt-get install apache2 -y
    sudo apt-get -y install python-dev python-pip
    sudo pip install wiringpi
    git clone https://github.com/silvanmelchior/RPi_Cam_Web_Interface.git
    sudo mv uconfig /var/www/html
    sudo mv php/getMediaSaved.php /var/www/html
    sudo mv microscope_led_server/ /opt
    sudo mv welab_4_makers /etc/init.d
    chmod +x /etc/init.d/welab_4_makers
    sudo systemctl enable welab_4_makers
    chmod u+x RPi_Cam_Web_Interface/RPi_Cam_Web_Interface_Installer.sh
    RPi_Cam_Web_Interface/RPi_Cam_Web_Interface_Installer.sh install
    sudo reboot
else
    echo "Please move the WeLAB-4-makers folder to /home/pi and run the script again."
fi