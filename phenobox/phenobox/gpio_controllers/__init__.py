import RPi.GPIO as GPIO

from input_controller import InputController, DoorState, ButtonPress
from led_controller import LedController
from motor_controller import MotorController

GPIO.setmode(GPIO.BCM)


def clean():
    """
    Cleans up all used GPIO pins and resets them to their default state.
    Should be called after all controllers are shut down before exiting the program
    """
    GPIO.cleanup()
