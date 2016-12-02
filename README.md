# WeLAB-4-makers

The software that lets you use your _We-LAB 4 makers_ kit is made of a Kivy GUI, a video streaming library (_RPi-Cam_web-Interface_ - available at https://github.com/silvanmelchior/RPi_Cam_Web_Interface) and a Python server that lets the GUI manage the intensity of the microscope led. In addition, there is a PHP script that enables the GUI to save pictures of the microscope view.

To set your _We-LAB 4 makers_ kit up, connect your Raspberry Pi to the internet, open the terminal and follow the next steps.

1 . If you have not done it before, expand the file system by running _raspi-config_ command, and reboot.
```
pi@raspberrypi ~ $ sudo raspi-config
pi@raspberrypi ~ $ sudo reboot
```

2 . Update the firmware, reboot and enable the camera by running _raspi-config_ command and choosing the _Enable Camera_ option. Also, choose _Advanced Options_ then _Memory Split_ and insert _256_ to increase the amount of memory available to the GPU.
```
pi@raspberrypi ~ $ sudo rpi-update
pi@raspberrypi ~ $ sudo reboot
pi@raspberrypi ~ $ sudo raspi-config
```

3 . To avoid the camera led interfere with the microscope led, disable the former by adding _disable_camera_led=1_ to the _/boot/config.txt_ file
```
pi@raspberrypi ~ $ sudo nano /boot/config.txt
```

4 . Clone the project folder from GitHub to the home directory (to go to the home, use command ```cd /home/pi```):
```
pi@raspberrypi:~ $ git clone https://github.com/DNAPhone/WeLAB-4-makers.git
```

5 . Go to the downloaded folder
```
pi@raspberrypi:~ $ cd WeLAB-4-makers
```

Now, you can use our setup script as described in step 6a, or follow the instructions at step 6b. However, if you already have RPi_Cam_Web_Interface installed, follow the steps at point 6b, but skips the library installation. Please note that while the RPi-Cam-Web-Interface library gets installed, it will prompt you a couple of times. Just hit ENTER (the first time it will start the installation process, the second will set the path to where images are saved). At the end, reboot the Raspberry Pi.

6a . (Alternative to step 6b) Change the setup script execution permission and run it. Please note that if you have already  installed _RPi_Cam_Web_Interface_, you have to remove from the setup script the lines that install it: _git clone https://github.com/silvanmelchior/RPi_Cam_Web_Interface.git_, _chmod u+x RPi_Cam_Web_Interface/RPi_Cam_Web_Interface_Installer.sh_, _RPi_Cam_Web_Interface/RPi_Cam_Web_Interface_Installer.sh install_. Also, you have to write the correct _RPi_Cam_Web_Interface_ install dir at line _sudo mv php/getMediaSaved.php RPi_Cam_Web_Interface_.
```
pi@raspberrypi:WeLAB-4-makers $ chmod u+x setup.sh
pi@raspberrypi:WeLAB-4-makers $ sudo ./setup.sh
```

6b . Steps alternative to step 6b

6b.1 . Update everything
```
pi@raspberrypi ~ $ sudo apt-get update && sudo apt-get upgrade -y
```

6b.2 . Install required packages
```
pi@raspberrypi ~ $ sudo apt-get -y install python-dev python-pip
```

6b.3 . Install wiringpi to manage the microscope led
```
pi@raspberrypi ~ $ sudo pip install wiringpi
```

6b.4 . If you do not have RPi_Cam_Web_Interface, download it
```
pi@raspberrypi ~ $ git clone https://github.com/silvanmelchior/RPi_Cam_Web_Interface.git
```

6b.5 . Copy our php file that allows image management to RPi_Cam_Web_Interface folder
```
pi@raspberrypi ~ $ sudo mv php/getMediaSaved.php /var/www/html
```

6b.6 . Set the server that receives led management commands
```
pi@raspberrypi ~ $ sudo mv microscope_led_server/ /opt
pi@raspberrypi ~ $ sudo mv welab_4_makers /etc/init.d
pi@raspberrypi ~ $ sudo mv uconfig /var/www/html
pi@raspberrypi ~ $ chmod +x /etc/init.d/welab_4_makers
pi@raspberrypi ~ $ sudo systemctl enable welab_4_makers
```

6b.7 . Finally, install RPi_Cam_Web_Interface
```
pi@raspberrypi:RPi_Cam_Web_Interface ~ $ cd RPi_Cam_Web_Interface
pi@raspberrypi:RPi_Cam_Web_Interface ~ $ chmod u+x RPi_Cam_Web_Interface/RPi_Cam_Web_Interface_Installer.sh
pi@raspberrypi:RPi_Cam_Web_Interface ~ $ RPi_Cam_Web_Interface/RPi_Cam_Web_Interface_Installer.sh install
```

6b.8. Reboot
```
pi@raspberrypi:RPi_Cam_Web_Interface ~ $ sudo reboot
```

7 . Retrieve the ip address of your Raspberry Pi using _ifconfig_ command. Search the output for the wlan interface and write somewhere the _inet addr_ value (in the following ecample it is 192.168.1.2).
```
pi@raspberrypi:kivy_interface ~ $ sudo kivy WeLAb.py
...
wlan0 ...
      inet addr:192.168.1.2
...
```

8 . Now copy kivy_interface folder on another computer in the network and run the GUI.
```
pi@raspberrypi:kivy_interface ~ $ sudo kivy WeLAb.py
```

Retrieve the ip address of your Raspberry Pi using ifconfig command, and write it to the GUI's settings (3rd tab).

When you take pictures of the microscope view, the Raspberry stores the original ones in /var/www/html/media. You may want to periodically check for the space they are taking and remove the ones you do not need to backup. On your computer, such images are stored in the folder specified by the GUI's settings.


# Kivy

Why Kivy? Because it is a powerful, open-source and cross-platform framework for the development of applications.

You can adapt and run the same code on all supported platforms.

You can use our GUI both remotely (via ethernet or wi-fi connection) or locally on a the same Raspberry Pi that operate the microscope camera.

Please refer to https://kivy.org/docs/installation/installation.html for detailed Kivy instruction for Linux, OSX and Windows operating systems.

Please  refefer to https://kivy.org/docs/installation/installation-rpi.html for detailed Kivy instruction for Raspberry Pi. 

In case of troubles running our interface directly on the Raspberry Pi, please follow the next tips (tested on a Raspberry Pi 3 running a fresh installation of Raspian Jessie with Pixel, Sept. 2016 version):

- Recent Kivy versions require Cython version 0.23 or newer. Jessie is currently provided with version 0.21, so be aware that you may need to update  the package. 

Please check the current Cython version:
```
dpkg -s cython
```

If the version is older than 0.23, replace it:
```
sudo pip uninstall cython
sudo pip install -I Cython==0.23
```

We installed all required dependencies as suggested on the Kivy website:
```
sudo apt-get update 
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
pkg-config libgl1-mesa-dev libgles2-mesa-dev python-setuptools libgstreamer1.0-dev \
git-core gstreamer1.0-plugins-{bad,base,good,ugly} gstreamer1.0-{omx,alsa} python-dev
```

Then we built Kivy:
```
git clone https://github.com/kivy/kivy 
cd kivy  
make 

echo "export PYTHONPATH=$(pwd):\$PYTHONPATH" >> ~/.profile 
source ~/.profile
 ```
 
As post-install settings, add some more external components:
```
sudo pip install pyglet docutils  
sudo pip install pygments 
```

Finally, in order to make the mouse visible edit the Kivy configuration file
```
sudo nano ~/.kivy/config.ini  
```
adding the following line at the bottom of the file, in the [modules] section:
```
touchring = show_cursor=true
```

To run the GUI, go to _kivy\_interface_ folder and run it as follows:
```
cd /home/pi/WeLAB-4-makers/kivy_interface
python WeLAb.py
```

Alternatively, you can try _kivy pie_, a compact and lightweight Raspbian-based distribution that comes with Kivy installed and ready to run (http://kivypie.mitako.eu).

Please be aware that Kivy under Raspbian should present some problems or limitations. Some interesting discussions are reported here:

- https://www.raspberrypi.org/forums/viewtopic.php?f=32&t=124181

- https://groups.google.com/forum/#!topic/kivy-users/_CKVtjSHC3w

- http://stackoverflow.com/questions/35083935/cant-close-kivy-app-or-avoid-fullscreen

- https://www.raspberrypi.org/forums/viewtopic.php?t=121013

Relevant issues we have experienced : 

- the GUI only works in fullscreen mode. This is not a _real_ problem, but it should be annoying because we have not (YET!!!) added a gallery section to the GUI...

- there’s the bubbling of  mouse events. In order to overcome possible troubles we suggest to tip the option _hide  the taskbar when not used_ in taskbar raspbian settings.
