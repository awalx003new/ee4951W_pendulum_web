#!/usr/bin/env python
from System.motor import Motor
from System.encoder import Encoder
import math
from datetime import datetime
from time import sleep
import RPi.GPIO as GPIO
import sys
import os
from threading import Thread, Lock

# IO pin definitions
### Motor pins
motor_speed_pin = 17
motor_forward_pin = 27
motor_reverse_pin = 22
### Encoder pins (shared by both encoders)
encoder_clock_pin = 2
encoder_data_pin = 3
### Angular encoder pins
encoder_angular_cs_pin = 4
### Linear encoder pins
encoder_linear_cs_pin = 14
### Limit switch pins (configured to PULLUP)
limit_negative_pin = 19
limit_positive_pin = 26

# System parameters
system_max_x = 16.5
system_min_x = -16.5

# System Class
# This is the primary interface a student will use to control the pendulum.
class System:
    def __init__(self, negative_limit=float('nan'), positive_limit=float('nan'), angular_units='Degrees', sw_limit_routine=None):
        GPIO.setwarnings(False)
        self.deinit = False
        # Initialize public variables
        self.max_x = system_max_x
        self.min_x = system_min_x
        # Initialize the motor.
        self.motor = Motor(motor_speed_pin, motor_forward_pin, motor_reverse_pin)
        # Initialize the angular encoder.
        self.encoder_angular = Encoder(encoder_clock_pin, encoder_angular_cs_pin, encoder_data_pin)
        self.encoder_angular.set_zero(offset = 512) # set offset so that 0 is upright vertical
        # Initialize the linear encoder.
        self.encoder_linear = Linear_Encoder(encoder_clock_pin, encoder_linear_cs_pin, encoder_data_pin)
        # We assume that the system has been initialized on startup to a 0 position, or that the previous run ended by returning the system to 0
        self.encoder_linear.set_zero()
        
        self.angular_units = angular_units
        
        # Enable hardware interrupts for hardware limit switches
        GPIO.setup(limit_negative_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(limit_negative_pin, GPIO.FALLING, callback=self.negative_limit_callback)
        GPIO.setup(limit_positive_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(limit_positive_pin, GPIO.FALLING, callback=self.positive_limit_callback)
        self.interrupted = False
        
        # Setup soft limits if defined by the user (this is "challenge mode" for the user, making the constraints more difficult).
        # By default, the soft limits will not be used (when set NaN), and the whole extent of the system is available (to the HW limits).
        self.negative_soft_limit = negative_limit
        self.positive_soft_limit = positive_limit
        # If both limits have been defined, verify that they are valid (i.e. positive limit must be greater than the negative limit)
        if not math.isnan(negative_limit) and not math.isnan(positive_limit) and not negative_limit < positive_limit:
            print("ERROR: Invalid software limits provided. Must be valid floating-point numbers and positive limit must be greater than negative limit. Software limits will be disabled.")
            self.negative_soft_limit = float('nan')
            self.positive_soft_limit = float('nan')
        # NOTE: If only one limit has been defined, this should always work (hardware limits will be the absolute edge on the undefined side, although this would be difficult for users to utilize unless we provide the position of the hardware limits on each side
        # NOTE: If neither limit is defined, the hardware limits will be the only limits in effect.
        self.sw_limit_routine = self.limit_triggered
        if sw_limit_routine is not None:
            self.sw_limit_routine = sw_limit_routine
        
        # Create and setup results file (to be sent back to the server and displayed/downloaded to the user)
        # Results file is a CSV with the following entries: angle, position, speed
        self.result_filename = "Results/" + os.path.basename(sys.argv[0]).split('.')[0] + "_results.csv"
        
        result_file = open(self.result_filename, "w+")
        result_file.write("timestamp,angle(" + angular_units + "),position(inches),speed(percentage)\n")
        result_file.close()
        
        # Setup a thread to constantly be measuring encoder positions
        #self.encoder_thread = EncoderThread(instance = self)
        self.encoder_thread = Thread(target = self.encoder_thread_routine)
        self.encoder_thread.setDaemon(True)
        self.angular_position = 0.
        self.linear_position = 0.
        self.encoder_thread.start()
    # END __init__()
    
    # Destructor
    # Brake the motor and call GPIO.cleanup as a last-chance of doing so
    def __del__(self):
        self.motor.brake()
        GPIO.cleanup()
    # END __del__()
    
    def initialize(self):
        # Temporarily disable the limit switch interrupts: we do not want the program to exit if the switch is triggered
        GPIO.remove_event_detect(limit_negative_pin)
        GPIO.remove_event_detect(limit_positive_pin)
        # Begin moving slowly in the negative direction until the negative limit switch is triggered
        if not GPIO.input(limit_negative_pin) == False:
            self.motor.move(-5)
            pressed = True
            while pressed != False:
                pressed = GPIO.input(limit_negative_pin)
                sleep(0.01)
        self.motor.brake()
        # Set zero at the negative end of the track for easy reference in determining the extent
        self.encoder_linear.set_zero()
        sleep(1)
        # Begin moving slowly in the positive direction until the positive limit switch is triggered
        self.motor.move(5)
        pressed = True
        while pressed != False:
            # We must continue reading linear encoder motion to keep track of rotations
            pressed = GPIO.input(limit_positive_pin)
            sleep(0.01)
        self.motor.brake()
        # Get the current position (the extent of the track)
        extent = self.linear_position
        # Move back towards the center until we reach position extent/2
        position = extent
        sleep(1)
        self.motor.move(-4)
        while position >= (extent / 2.):
            position = self.linear_position
            sleep(0.015) 
        self.motor.brake()
        # Set zero again: this is the real zero
        self.encoder_linear.set_zero()
        # Re-enable the limit switch interrupts
        GPIO.add_event_detect(limit_negative_pin, GPIO.FALLING, callback=self.negative_limit_callback, bouncetime=300)
        GPIO.add_event_detect(limit_positive_pin, GPIO.FALLING, callback=self.positive_limit_callback, bouncetime=300)
    # END initialize
    
    # Return home, cleanup IO. This should be called when exiting the program
    def deinitialize(self):
        self.return_home()
        self.motor.brake()
        self.deinit = True
        if self.encoder_thread.isAlive():
            self.encoder_thread.join()
        sleep(1)
        GPIO.cleanup()
    
    # Get the values of the encoders to determine the angular and linear position of the pendulum.
    # Values are returned as a tuple: (angle, linear).
    ### angle: 0 indicates the pendulum is exactly straight up.
    #####      180 or -180 indicate the pendulum is exactly straight down.
    #####      Positive values indicate the pendulum is leaning to the right.
    #####      Negative values indicate the pendulum is leaning to the left.
    ### linear: 0 indicates the pendulum is exactly in the middle of the track.
    #####       Positive values indicate the pendulum is right-of-center.
    #####       Negative values indicate the pendulum is left-of-center.
    def measure(self):
        return (self.angular_position, self.linear_position)
    # END measure()
    
    
    # Thread routine (0.1s interval). Get the values of the encoders to determine the angular and linear position of the pendulum.
    # Values are saved in the class (self.angular_position and self.linear_position), which are then simply returned by measure()
    def encoder_thread_routine(self):
        limit_serviced = False
        while self.deinit == False:
            angular_position = self.encoder_angular.read_position(self.angular_units)
            if self.angular_units == 'Degrees':
                if angular_position > 180.:
                    angular_position = angular_position - 360.
            self.angular_position = angular_position
            self.linear_position = self.encoder_linear.read_position()
            # Check soft limits
            if (not math.isnan(self.negative_soft_limit)) and self.linear_position < self.negative_soft_limit: #or self.linear_position < self.min_x:
                if limit_serviced == False:
                    limit_serviced = True
                    # SW limit reached: stop the motor, set the interrupted flag so that the motor cannot continue to move until the interrupt has been completely serviced
                    #self.interrupted = True
                    self.motor.brake()
                    # Print negative soft limit violation to the results file.
                    result_file = open(self.result_filename, "a")
                    result_file.write("Negative software limit %f has been reached!\n" % self.negative_soft_limit)
                    result_file.close()
                    # Fire the limit trigger method
                    self.sw_limit_routine()
            elif (not math.isnan(self.positive_soft_limit)) and self.linear_position > self.positive_soft_limit: #or self.linear_position > self.max_x:
                if limit_serviced == False:
                    limit_serviced = True
                    # SW limit reached: stop the motor, set the interrupted flag so that the motor cannot continue to move until the interrupt has been completely serviced
                    #self.interrupted = True
                    self.motor.brake()
                    # Print positive soft limit violation to the results file.
                    result_file = open(self.result_filename, "a")
                    result_file.write("Positive software limit %f has been reached!\n" % self.positive_soft_limit)
                    result_file.close()
                    # Fire the limit trigger method
                    self.sw_limit_routine()
            elif limit_serviced == True and self.linear_position > (self.negative_soft_limit+0.5) and self.linear_position < (self.positive_soft_limit-0.5):
                # Clear the limit service flag once we return to a reasonable range that the limit will not trigger again
                limit_serviced = False
            # This thread should run on ~0.01s intervals
            sleep(0.01)
    
    # Adjust the pendulum's linear position using the motor.
    ### speed: Acceptable values range from -100 to 100 (as a percentage), with 100/-100 being the maximum adjustment speed.
    #####      Negative values will move the pendulum to the left.
    #####      Positive values will move the pendulum to the right.
    def adjust(self, speed):
        if self.interrupted == False:
            if speed != 0:
                # cap the speed inputs
                if speed > 100.:
                    speed = 100.
                if speed < -100.:
                    speed = -100.
                # change the motor speed
                # TODO: Make sure the motor is oriented so that positive speed the correct direction (same for negative). Change the values otherwise.
                self.motor.coast()
                self.motor.move(speed)
            else:
                self.motor.coast()
    # END adjust()
    
    # Append data to the results file
    def add_results(self, angle, position, speed):
        # open the results file
        result_file = open(self.result_filename, "a")
        # Write the results
        result_file.write("%s," % datetime.now().strftime("%H:%M:%S.%f"))   # Write current time
        result_file.write("%f," % angle)                                    # Write angle
        result_file.write("%f," % position)                                 # Write position
        result_file.write("%f\n" % speed)                                   # Write speed (end of line)
        # Close the results file
        result_file.close()
    # END add_results
    
    def add_log(self, message):
        # open the results file
        result_file = open(self.result_filename, "a")
        # Write the log
        result_file.write("%s\n" % message)
        # re-write the csv headers for next logging
        result_file.write("timestamp,angle(" + self.angular_units + "),position(inches),speed(percentage)\n")
        # Close the results file
        result_file.close()
    
    # Go back to the zero position (linear) so that the next execution starts in the correct place.
    def return_home(self):
        position = self.linear_position
        # slowly move towards 0 until we get there
        if position > 0:
            self.motor.move(-4)
            while position > 0:
                position = self.linear_position
                sleep(0.015)
            self.motor.brake()
            return
        else:
            self.motor.move(4)
            while position < 0:
                position = self.linear_position
                sleep(0.015)
            self.motor.brake()
            return
    # END return_home
    
    # Callback for when negative limit switch is triggered.
    def negative_limit_callback(self, channel):
        self.interrupted = True
        self.motor.brake()
        # Print negative limit trigger to the results file.
        result_file = open(self.result_filename, "a")
        result_file.write("Negative hardware limit has been reached!\n")
        result_file.close()
        # Fire the limit trigger method (stops motor, kills program immediately).
        self.limit_triggered()
    # END negative_limit_callback
    # Callback for when positive limit switch is triggered.
    def positive_limit_callback(self, channel):
        self.interrupted = True
        self.motor.brake()
        # Print positive limit trigger to the results file.
        result_file = open(self.result_filename, "a")
        result_file.write("Positive hardware limit has been reached!\n")
        result_file.close()
        # Fire the limit trigger method (stops motor, kills program immediately).
        self.limit_triggered()
    # END positive_limit_callback
    def limit_triggered(self):
        sleep(1)
        self.deinitialize()
        sys.exit(1)
# END System

# Linear Encoder class
# This class is to help with using an absolute encoder for linear position sensing as assembled in the physical system.
# The function definitions here are the same as with the regular encoder (pseudo-interface).
class Linear_Encoder:
    PROPORTION = 14.5
    
    def __init__(self, clk_pin, cs_pin, data_pin):
        self.encoder = Encoder(clk_pin, cs_pin, data_pin)
        self.set_zero()
    def set_zero(self):
        # Set the zero position for the encoder
        self.encoder.set_zero()
        # Reset the internal position counter
        self.rotations = 0.
        self.last_position = 0.
    def read_position(self):
        # Read the position of the encoder (apply a noise filter, we don't need that much precision here)
        position = float(self.encoder.read_position('Raw') & 0b1111111100)
        # Compare to last known position
        # NOTE: For now, assume that we are moving the smallest possible distance (i.e. 5 -> 1 is -4, not 1020)
        if (position - self.last_position) > 768.:
            self.rotations = self.rotations - 1.
        elif (position - self.last_position) < -768.:
            self.rotations = self.rotations + 1.
        
        # Save the last position for the next calculation
        self.last_position = position 
        # compute the position based on the system parameters
        # linear position = (2pi*r)(n) + (2pi*r)(position/1024) = (2pi*r)(n + position/1024) = (pi*d)(n + position/1024)
        return (self.PROPORTION)*(self.rotations + position/1024.)
