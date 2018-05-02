import os

import time

import sys

import photobox
from config import config

config.load_config('{}/{}'.format('config', 'production_config.ini'))
while not os.path.ismount(getattr(config, 'cfg').get('box', 'shared_folder_mountpoint')):
    time.sleep(1)

photobox.run()
