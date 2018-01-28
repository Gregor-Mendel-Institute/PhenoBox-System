import logging
from time import time

from RPi import GPIO
from enum import Enum


class DoorState(Enum):
    OPEN = 1
    CLOSED = 2


class ButtonPress(Enum):
    SHORT = 1
    LONG = 2


class InputController:
    _START_BUTTON = 12  #:GPIO Pin to which the start button is connected
    _DOOR_CONTACT = 4  #:GPIO Pin to which the door contact switch is connected
    _door_closed = True

    _start_pressed = 0
    _start_released = 0

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self.door_cb = None
        self.button_cb = None

    def initialize(self, door_state_changed_cb=None, start_button_cb=None):
        """
        Sets up all GPIO pins and attaches the according callback methods
        :return:
        """
        GPIO.setup(self._START_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._DOOR_CONTACT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self._door_closed = True if (GPIO.input(self._DOOR_CONTACT) == GPIO.LOW) else False

        self.door_cb = door_state_changed_cb
        self.button_cb = start_button_cb

        GPIO.add_event_detect(self._DOOR_CONTACT, GPIO.BOTH, callback=self.door_state_changed)
        GPIO.add_event_detect(self._START_BUTTON, GPIO.BOTH, callback=self.evaluate_start, bouncetime=40)

    def get_door_state(self):
        return DoorState.OPEN if GPIO.input(self._DOOR_CONTACT) == GPIO.HIGH else DoorState.CLOSED

    def register_door_state_changed_cb(self, cb):
        self.door_cb = cb

    def register_start_button_cb(self, cb):
        self.button_cb = cb

    def door_state_changed(self, channel):
        """
        Callback method to check if the door has been opened or closed.
        Invokes the registered callback and passes either DoorState.OPen or DoorState.CLOSED depending on the door state

        This method should be invoked on RISING and FALLING edge changes

        :param channel: The GPIO Pin on which the change happened

        :return: None
        """
        if GPIO.input(channel) == GPIO.HIGH:
            if self.door_cb:
                self.door_cb(DoorState.OPEN)
            if self._door_closed:
                self._door_closed = False
        elif GPIO.input(channel) == GPIO.LOW:
            if self.door_cb:
                self.door_cb(DoorState.CLOSED)
            self._logger.info('Door closed')
            self._door_closed = True

    def evaluate_start(self, channel):
        """
        Callback method to check for presses of the start button and distinguish between a short and a long press and
        call the registered callback method with ButtonPress.LONG or SHORT accordingly
        This method should be invoked on RISING and FALLING edge changes

        :param channel: The GPIO Pin on which the change happened

        :return: None
        """
        if GPIO.input(channel) == GPIO.LOW:
            self._start_pressed = time()
        elif GPIO.input(channel) == GPIO.HIGH:
            self._start_released = time()
            elapsed = self._start_released - self._start_pressed
            if elapsed > 3:
                self._logger.info('Long press detected')
                if self.button_cb:
                    self.button_cb(ButtonPress.LONG)
            else:
                self._logger.info('Short press detected')
                if self.button_cb:
                    self.button_cb(ButtonPress.SHORT)
            self._start_pressed = 0
            self._start_released = 0
