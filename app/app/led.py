import RPi.GPIO as GPIO
import time
# Use GPIO pins on Raspberry Pi
i=2
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7,GPIO.OUT)
GPIO.output(7, GPIO.HIGH)
time.sleep(5)
GPIO.output(7, GPIO.LOW)
