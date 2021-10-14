# Import required modules
import RPi.GPIO as GPIO
import time
import math

# Constants: parameters that the caller cannot modify
# Delay: Minimum delay necessary after pull pin low to read input
delay = 0.0000005

# Encoder Class
# This controls the motor at the given IO
class Encoder:
    def __init__(self, clk_pin, cs_pin, data_pin):
        # Set the board IO (just in case it hasn't been done yet)
        GPIO.setmode(GPIO.BCM)
        # Setup class varaiable
        self.offset = 0
        self.clk_pin = clk_pin
        self.cs_pin = cs_pin
        self.data_pin = data_pin
        # Setup the IO
        try:
            GPIO.setup(self.clk_pin, GPIO.OUT)
            GPIO.setup(self.cs_pin, GPIO.OUT)
            GPIO.setup(self.data_pin, GPIO.IN)
            # Setup the CS and CLK to be high
            GPIO.output(PIN_CLK, 1)
            GPIO.output(PIN_CS, 1)
        except:
            # If this fails, it's likely because the IO has already been configured. The encoders share some pins. Ignore the failure
            time.sleep(0.01) # Used just to have something in the exception catch
            #print("ERROR. Unable to setup the configuration required")
        # Wait some time to before reading
        time.sleep(0.5)
    def set_zero(self, offset = 0):
        # Take current position as zero
        pos = self.read_position('Raw')
        self.offset = (self.read_position('Raw') + self.offset + offset) % 1024
    def clockup(self):
        GPIO.output(self.clk_pin, 1)
    def clockdown(self):
        GPIO.output(self.clk_pin, 0)
    def read_position(self, format):
        # Most of this is based of timing diagram of encoder
        # Pull CS low to start reading
        GPIO.output(self.cs_pin, 0) 
        # Delay necessary before reading is ready
        time.sleep(delay*2)
        data = 0
        # Clockdown necessary before reading 
        self.clockdown()
        # Go through 10 bits needed to read
        for i in range(0, 10): 
            # Clock up to start reading one bit
            self.clockup()
            # Shift data left and insert input 
            data <<= 1  
            data |= GPIO.input(self.data_pin)
            # Clock down after finish reading
            self.clockdown()
        # Pull CS high after finish reading
        GPIO.output(self.cs_pin, 1)
        # Format with offset, Max is 1024
        data = (data - self.offset) % 1024
        # Data is linearly mapped
        if format=="Raw":
            return data
        elif format == "Degrees":
            degrees = (data/1024.0) * 360.0
            return degrees
        elif format == "Radians":
            radians = (data/1024.0) * (2.0*math.pi)
            return radians
        else:
            print("ERROR. Invalid format (Raw, Degrees, Radians)")
            return None
    
