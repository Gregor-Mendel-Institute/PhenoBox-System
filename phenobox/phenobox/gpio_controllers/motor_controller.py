import time

import RPi.GPIO as GPIO


class MotorController:
    """
    Class to control the connected motor LER10K via its motor controller LECP6 PNP
    All lines, except the ALARM line are active high.
    """
    # Pin declarations
    #: The GPIO Pin to which the SVON line of the motor controller is connected. Used to turn the servo on. Active High.
    _SVON = 17
    #: The GPIO Pin to which the IN0 line of the motor controller is connected. Used to send position to the controller
    _IN0 = 22
    #: The GPIO Pin to which the IN1 line of the motor controller is connected. Used to send position to the controller
    _IN1 = 23
    #: The GPIO Pin to which the IN2 line of the motor controller is connected. Used to send position to the controller
    _IN2 = 24
    #: The GPIO Pin to which the ENABLE line of the motor controller is connected. Used to enable to controller.
    _ENABLE = 26
    #: The GPIO Pin to which the SETUP line of the motor controller is connected. Used to initialize the motor controller on startup
    _SETUP = 27
    #: The GPIO Pin to which the DRIVE line of the motor controller is connected. Used to start a movement. Active High
    _DRIVE = 18
    #: The GPIO Pin to which the RESET line of the motor controller is connected. Used to reset the Alarm state.
    _RESET = 25

    #: The GPIO Pin to which the ALARM line of the motor controller is connected. If this gets low the motor emits an ALARM condition
    _ALARM = 21
    #: The GPIO Pin to which the INP line of the motor controller is connected. Used by the controller to signal that it has reached the target position
    _INP = 20
    #: The GPIO Pin to which the SVRE line of the motor controller is connected. Used by the controller to indicate that the servo is ready
    _SVRE = 16

    # TODO listen for ALARM signal of motor controller and take actions accordingly (transition to error)
    # Pass in a callback to the initialize function which should get called when the ALARM is triggered (Gets low)

    def __init__(self):
        self._current_angle = -1

    def _wait_until(self, pin, state):
        """
        Waits for the pin to reach the given state

        :param pin: The GPIO pin to watch
        :param state: The state in which the given pin should change to

        :return:None
        """
        time.sleep(0.4)
        while GPIO.input(pin) != state:
            pass

    def initialize(self):
        """
        Sets up all necessary GPIO pins.
        Resets the inital alarm state of the motor controller.
        Returns the motor to its origin position

        :return: None
        """
        GPIO.setup(self._ENABLE, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self._SVON, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self._IN0, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self._IN1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self._IN2, GPIO.OUT, initial=GPIO.LOW)

        GPIO.setup(self._SETUP, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self._DRIVE, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self._RESET, GPIO.OUT, initial=GPIO.LOW)

        GPIO.setup(self._ALARM, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._INP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._SVRE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        time.sleep(2)
        if not GPIO.input(self._ALARM):  # ALARM is negative logic
            print "RESET ALARM"
            GPIO.output(self._RESET, GPIO.HIGH)
            self._wait_until(self._ALARM, GPIO.HIGH)
            GPIO.output(self._RESET, GPIO.LOW)
            print "ALARM RESET"

        GPIO.output(self._ENABLE, GPIO.HIGH)
        GPIO.output(self._SVON, GPIO.HIGH)
        self._wait_until(self._SVRE, GPIO.HIGH)
        GPIO.output(self._SETUP, GPIO.HIGH)
        self._wait_until(self._INP, GPIO.HIGH)
        GPIO.output(self._SETUP, GPIO.LOW)
        GPIO.output(self._SVON, GPIO.LOW)
        self._current_angle = 0

    def return_to_origin(self):
        """
        Used to move the motor to its 0 position which should be programmed to be the origin position
        This method blocks until the motor has reached the position

        :return: None
        """
        self.move_to_position(0)

    @property
    def current_angle(self):
        """
        Property to get the current angle of the motor relative to its origin position

        :return: The current angle
        """
        return self._current_angle

    def move_to_position(self, position):
        """
        Takes in a number indicating the position index and moves the motor to the corresponding position which is programmed
        into the motor controller.
        This method blocks until the motor has reached the given position.

        :param position: The index of the position to move the motor to

        :return: None
        """
        if 0 <= position < 6:
            self._current_angle = -1
            GPIO.output(self._SVON, GPIO.HIGH)
            binary_position = '{0:03b}'.format(position)  # Convert to 3 bit binary number with leading 0s
            length = len(binary_position)
            in0_val = GPIO.LOW if int(binary_position[length - 1]) == 0 else GPIO.HIGH
            in1_val = GPIO.LOW if int(binary_position[length - 2]) == 0 else GPIO.HIGH
            in2_val = GPIO.LOW if int(binary_position[length - 3]) == 0 else GPIO.HIGH

            self._wait_until(self._SVRE, GPIO.HIGH)

            GPIO.output(self._IN0, in0_val)
            GPIO.output(self._IN1, in1_val)
            GPIO.output(self._IN2, in2_val)
            time.sleep(0.4)

            GPIO.output(self._DRIVE, GPIO.HIGH)
            self._wait_until(self._INP, GPIO.HIGH)
            GPIO.output(self._DRIVE, GPIO.LOW)
            GPIO.output(self._SVON, GPIO.LOW)
            self._current_angle = position * 60
