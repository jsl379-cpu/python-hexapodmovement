from dotenv import load_dotenv

from st3215 import ST3215
import time
import os

from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')
device = os.getenv('ST3215_DEV')
servo = ST3215(device)


print(servo.ReadPosition(3))
# the range servos can move is 0 - 4095
# important, please try not to move servos beyond limits that might break the pla carriage.

# sample usage:
# servo.MoveTo(1, 1500)  # moves servo with ID 1 to position 1500

