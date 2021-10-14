from system import System
from time import sleep
        
# Main program
sys = System()
sys.initialize()

ang,lin = sys.measure()
print("Starting position before moving: " + str(lin))
sys.adjust(4)
ang,lin = sys.measure()
sleep(0.01)
while lin < 10:
    ang,lin = sys.measure()
    sleep(0.01)
sys.return_home()
