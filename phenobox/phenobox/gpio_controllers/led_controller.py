import RPi.GPIO as GPIO

from blinker import Blinker


class LedController:
    #:GPIO Pin to which the green LED is connected
    _GREEN = 19
    #:GPIO Pin to which the blue LED is connected
    _BLUE = 13
    #:GPIO Pin to which the orange LED is connected
    _ORANGE = 6
    #:GPIO Pin to which the red LED is connected
    _RED = 5
    #: A dictionary to hold references to the active blinker instances to be able to stop them.
    blinkers = {
        _GREEN: None,
        _BLUE: None,
        _ORANGE: None,
        _RED: None
    }

    def __init__(self):
        pass

    def initialize(self):
        """
        Sets up all GPIO pins for controlling the LEDs

        :return: None
        """
        GPIO.setup(self._GREEN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self._BLUE, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self._ORANGE, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self._RED, GPIO.OUT, initial=GPIO.LOW)

    def clear_all(self):
        """
        Turns off all LEDs

        :return: None
        """
        self.switch_green(False)
        self.switch_blue(False)
        self.switch_orange(False)
        self.switch_red(False)

    def _stop_blinker(self, pin):
        """
        Stops the blinker Thread for the given pin if it

        :param pin: The pin for which the blinker should be stopped

        :return: None
        """
        # TODO implement an asynchronus version of this with a callback method once its finished
        blinker = self.blinkers[pin]
        if blinker is not None:
            blinker.stop()
            blinker.join()  # Necessary to avoid race conditions

    def _blink(self, pin, interval):
        """
        Set up a blinker for the given pin with the specified interval

        :param pin: The pin to which the LED to blink is connected
        :param interval: The interval (in seconds) at which the LED should blink

        :return: None
        """
        self._stop_blinker(pin)
        blinker = Blinker(pin, interval)
        blinker.start()
        self.blinkers[pin] = blinker

    # TODO implement the possibility to blink multiple LEDs with one blinker Thread to prevent drifting
    def blink_green(self, interval=2):
        """
        Blink the green LED at the given interval

        :param interval: The interval (in seconds) at which the LED should blink (optional, default: 2seconds)

        :return: None
        """
        self._blink(self._GREEN, interval)

    def blink_blue(self, interval=2):
        """
        Blink the blue LED at the given interval

        :param interval: The interval (in seconds) at which the LED should blink (optional, default: 2seconds)

        :return: None
        """
        self._blink(self._BLUE, interval)

    def blink_orange(self, interval=2):
        """
        Blink the orange LED at the given interval

        :param interval: The interval (in seconds) at which the LED should blink (optional, default: 2seconds)

        :return: None
        """
        self._blink(self._ORANGE, interval)

    def blink_red(self, interval=2):
        """
        Blink the red LED at the given interval

        :param interval: The interval (in seconds) at which the LED should blink (optional, default: 2seconds)

        :return: None
        """
        self._blink(self._RED, interval)

    def switch_green(self, on=False):
        """
        Switches the green LED to the given state.

        :param on: The state to be switched to. True for on, False for off (optional, default: False)

        :return: None
        """
        self._stop_blinker(self._GREEN)
        val = GPIO.HIGH if on else GPIO.LOW
        GPIO.output(self._GREEN, val)

    def switch_blue(self, on=False):
        """
        Switches the green LED to the given state.

        :param on: The state to be switched to. True for on, False for off (optional, default: False)

        :return: None
        """
        self._stop_blinker(self._BLUE)
        val = GPIO.HIGH if on else GPIO.LOW
        GPIO.output(self._BLUE, val)

    def switch_orange(self, on=False):
        """
        Switches the orange LED to the given state.

        :param on: The state to be switched to. True for on, False for off (optional, default: False)

        :return: None
        """
        self._stop_blinker(self._ORANGE)
        val = GPIO.HIGH if on else GPIO.LOW
        GPIO.output(self._ORANGE, val)

    def switch_red(self, on=False):
        """
        Switches the red LED to the given state.

        :param on: The state to be switched to. True for on, False for off (optional, default: False)

        :return: None
        """
        self._stop_blinker(self._RED)
        val = GPIO.HIGH if on else GPIO.LOW
        GPIO.output(self._RED, val)
