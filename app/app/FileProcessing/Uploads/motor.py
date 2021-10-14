#!/usr/bin/env python

# Import required modules
import RPi.GPIO as GPIO
from time import sleep

# Constants: parameters that the caller cannot modify
# Frequency: We have determined that the optimal frequency for our motor is 1kHz
pwm_frequency = 1000

# Motor Class
# This controls the motor at the given IO
class Motor:
    def __init__(self, speed_pin, forward_pin, reverse_pin):
        # Set the board IO (just in case it hasn't been done yet)
        GPIO.setmode(GPIO.BCM)
        # Set our variables for the directional pins
        self.forward_pin = forward_pin
        self.reverse_pin = reverse_pin
        # setup the IO
        GPIO.setup(speed_pin, GPIO.OUT)
        GPIO.setup(self.forward_pin, GPIO.OUT)
        GPIO.setup(self.reverse_pin, GPIO.OUT)
        # Set speed pin as a PWM output
        self.speed_pwm = GPIO.PWM(speed_pin, pwm_frequency)
        self.current_speed = 0.
    # END __init__
        
    # Move the motor at a given speed, given as a floating point percentage (-100 <= x <= 100)
    # If speed is less than 0, motor will run in reverse, otherwise it will run forward
    def move(self, speed):
        if speed == self.current_speed:
            # do not attempt to readjust speed; this can cause erratic behavior
            return
        if speed < -100.0 or speed > 100.0:
            return
        # Stop any previous movements
        self.speed_pwm.stop()
        # Set the duty cycle for the speed of the motor
        self.speed_pwm.ChangeDutyCycle(abs(speed))
        if speed < 0:
            # Set direction to reverse
            GPIO.output(self.forward_pin, GPIO.LOW)
            GPIO.output(self.reverse_pin, GPIO.HIGH)
        else:
            # Set the direction to forward
            GPIO.output(self.forward_pin, GPIO.HIGH)
            GPIO.output(self.reverse_pin, GPIO.LOW)
        # Start the PWM output to start moving the motor
        self.speed_pwm.start(abs(speed))
        self.current_speed = speed
        sleep((1./pwm_frequency) * 3)
    # END Move
    
    # Stop the motor from spinning.
    # To brake the motor, both direction outputs are set to HIGH
    def brake(self):
        # Stop any current PWM signals
        self.speed_pwm.stop()
        # Set the direction outputs to brake
        GPIO.output(self.forward_pin, GPIO.HIGH)
        GPIO.output(self.reverse_pin, GPIO.HIGH)
        self.current_speed = 0.
    # END Brake
        
    # Set the motor to coast (i.e. Do not provide power to the motor, but still allow it to spin)
    # To coast the motor, both direction outputs are set to LOW
    def coast(self):
        # Stop any current PWM signals
        self.speed_pwm.stop()
        # Set the direction outputs to coast
        GPIO.output(self.forward_pin, GPIO.LOW)
        GPIO.output(self.reverse_pin, GPIO.LOW)
        self.current_speed = 0.
    # END Coast
    