import logging
import subprocess
import sys
from Queue import Queue, Empty
from logging.handlers import RotatingFileHandler

from colorama import init, Fore

import gpio_controllers as gpio
from camera import CameraController
from config import config
from event import Event
from gpio_controllers import InputController, LedController, MotorController, DoorState, ButtonPress
from image_processing import CodeScanner
from machine import PhenoboxMachine
from network import TokenAuth
from network.image_handler import ImageHandler


class Phenobox():
    def __init__(self):
        self.phenobox_machine, self.motor_controller, self.led_controller, self.camera_controller, self.image_handler = self.initialize()
        self.input_controller = InputController()
        self.input_controller.initialize(self.door_state_changed, self.start_pressed)
        self.eventQueue = Queue()
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self.door_state = self.input_controller.get_door_state()

    def door_state_changed(self, state):
        """
        If it is opened while the box is not in the IDLE or ERROR state it will transition to the ERROR state

        :param state: The current/new DoorState

        :return: None
        """
        self.door_state = state
        if state == DoorState.OPEN:
            if not self.phenobox_machine.is_IDLE() and not self.phenobox_machine.is_ERROR():
                self._logger.info('Door Opened while running')
                self.phenobox_machine.door_opened(error_code=3)

    def start_pressed(self, press):
        if press == ButtonPress.SHORT:
            print(Fore.CYAN + "State: " + self.phenobox_machine.state)
        if self.phenobox_machine.is_IDLE() or self.phenobox_machine.is_ERROR():
            if press == ButtonPress.LONG:
                print(Fore.MAGENTA + "Shutdown Requested")
                self._logger.info('Shutdown action placed')
                self.eventQueue.put(Event.SHUTDOWN)
            else:
                if self.door_state == DoorState.CLOSED:
                    print(Fore.BLUE + "Start")
                    if self.phenobox_machine.is_IDLE():
                        self._logger.info('Start action placed')
                        self.eventQueue.put(Event.START)
                    else:
                        self._logger.info('Restart action placed')
                        self.eventQueue.put(Event.RESTART)
                else:
                    print(Fore.RED + "Please close the door before starting!")

    def initialize(self):
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = RotatingFileHandler(getattr(config, 'cfg').get('box', 'log_file'), maxBytes=5242880,
                                           backupCount=4)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)

        init(autoreset=True)

        photo_count = getattr(config, 'cfg').getint('box', 'photo_count')
        led_controller = LedController()
        led_controller.initialize()
        led_controller.blink_green(1)
        led_controller.blink_blue(1)
        scanner = CodeScanner()
        scanner.initialize()
        camera_controller = CameraController()
        camera_controller.initialize()
        motor_controller = MotorController()
        motor_controller.initialize()

        base_address = getattr(config, 'cfg').get('server', 'base_address')
        auth_address = '{}{}'.format(base_address, getattr(config, 'cfg').get('server', 'auth_endpoint'))
        reauth_address = '{}{}'.format(base_address, getattr(config, 'cfg').get('server', 'reauth_endpoint'))

        auth = TokenAuth(auth_address, reauth_address,
                         username=getattr(config, 'cfg').get('credentials', 'username'),
                         password=getattr(config, 'cfg').get(
                             'credentials', 'password'))

        image_handler = ImageHandler(photo_count=photo_count, auth=auth)
        image_handler.setDaemon(True)
        image_handler.start()

        phenobox_machine = PhenoboxMachine(camera_controller, scanner, motor_controller, led_controller, image_handler,
                                           auth,
                                           photo_count)
        phenobox_machine.initialize()
        return (phenobox_machine, motor_controller, led_controller, camera_controller, image_handler)

    def _terminate(self):
        self.led_controller.clear_all()
        self.camera_controller.close()
        self.led_controller.blink_green(interval=1)
        self.led_controller.blink_blue(interval=1)
        self.image_handler.stop()
        self.image_handler.join()
        self.led_controller.clear_all()
        gpio.clean()

    def run(self):
        # self.phenobox_machine, self.motor_controller, self.input_controller, self.led_controller, self.camera_controller, self.image_handler = self.initialize()
        shutdown = False
        try:
            while True:
                try:
                    event = self.eventQueue.get(True, 0.1)
                except Empty:
                    continue
                if event == Event.START:
                    self.phenobox_machine.start()
                if event == Event.RESTART:
                    self.phenobox_machine.restart()
                if event == Event.SHUTDOWN:
                    shutdown = True
                    break

        except KeyboardInterrupt:
            print "keyboard interrupt"
        print(Fore.MAGENTA + 'Shutdown initiated')
        self._terminate()
        if shutdown:
            subprocess.call(['sudo shutdown -h now "System halted by GPIO action" &'], shell=True)


if __name__ == '__main__':
    config.load_config('{}/{}'.format('config', sys.argv[1]))
    phenobox = Phenobox()
    phenobox.run()
