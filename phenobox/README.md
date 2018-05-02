# Phenobox

This folder contains the code which powers the phenobox itself. 

The code is intended to be deployed to a Raspberry Pi installed inside the box. 
Currently the only tested Pi is the Raspberry Pi 3 with the Raspbian distribution.

## Prerequisites

 * Assembled Phenobox
 * Raspberry Pi 3 running Raspbian
 * Network connection to the Phenopipe server
 * Network File Share (NFS) to store the taken images to
 
## Installation

 1. Allow the user pi access to the GPIO pins without sudo
     * Add a group called gpio and add the user pi to it
         ```bash
           sudo groupadd gpio
           sudo adduser pi gpio
          ```
     * Give this new group the necessary privileges for the according memory regions used to access the GPIO pins
         ```bash
          sudo chown root:gpio /dev/gpiomem
          sudo chmod g+rw /dev/gpiomem 
          ```
     * Finally if everything went right the permissions should look like this
         ```bash
           ls -l /dev/gpiomem 
           crw-rw---- 1 root gpio 244, 0 Nov 23 19:54 /dev/gpiomem
         ```
 1. Allow the user pi to shutdown the system without entering a password
     * use `visudo` to edit the sudoers file and add the following
     ```
        pi ALL=(ALL) NOPASSWD: /sbin/shutdown
     ```
 1. Automount the NFS on startup
     * Use an entry to /etc/fstab to accomplish this. Please refer to any tutorial on the web on how to do this.
 1. Install zBar
     ```bash
     sudo apt-get install libzbar-dev
     sudo apt-get install git-core
     sudo apt-get install python-dev 
     sudo pip install git+https://github.com/npinchot/zbar.git
     ```
 1. Install gphoto2
     * To install gphoto2 and libgphoto2 please use [gphoto2-updater](https://github.com/gonzalo/gphoto2-updater)
     * To install the python bindings use 
         ```bash
         pip install -v gphoto2
         ```
 1. Download the code under /phenobox from the repository onto the Pi and run the following in the root directory of the project
     ```bash
     pip install -r requirements
     ```
 1. Create a file called 'production_config.py' under 'phenobox/config' and fill it according to the 
     * For a sample config file consult the wiki
     
 1. Set up a cronjob for user pi to execute the autorun.sh script on reboot
   * Use the following to create a new cronjob
       ```bash
       sudo crontab -e -u pi
       ```
   * Enter the following to run the autorun python script contained in the repository on ever reboot
       ```
       @reboot cd /path/to/the/phenobox/application; /usr/bin/python autostart.py >> /home/pi/phenobox_cron.log 2>&1
       ```

# Further Information

Please refer to the corresponding wiki page: https://github.com/Gregor-Mendel-Institute/PhenoBox-System/wiki/phenobox-home
