# This file should be run on system startup. It will initialize the linear position to the center so that all tests originate from a proper position.
# The center is found by using the hardware limit switches
from system import System
import RPi.GPIO as GPIO
        
# Main program
sys = System()
sys.initialize()
GPIO.cleanup()
