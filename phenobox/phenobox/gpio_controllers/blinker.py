import threading

import time
from RPi import GPIO


class Blinker(threading.Thread):
    """
    Background thread to blink the status LEDs at given intervals

    """

    # TODO implement the possibility to blink multiple LEDs in the same thread
    def __init__(self, pin, interval=2):
        """

        :param pin: The GPIO pin to which the LED is connected
        :param interval: The interval to blink in seconds
        """
        super(Blinker, self).__init__()
        self._stop = threading.Event()
        self.pin = pin
        self.interval = interval
        self.state = True

    def stop(self):
        """
        Method to signal to the thread that it should stop.

        :return: None
        """
        self._stop.set()

    def stopped(self):
        """
        Returns a boolean value indicating whether or not this thread should stop

        :return: None
        """
        return self._stop.isSet()

    def run(self):
        """
        Blinks the given LED in the specified interval as long as the :meth:`.stop` method hasn't been called

        :return: None
        """
        while not self.stopped():
            GPIO.output(self.pin, self.state)
            self.state = not self.state
            time.sleep(self.interval)
