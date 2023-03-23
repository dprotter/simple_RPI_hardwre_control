from components import Switch, SwitchManager, Box, ContinuousServo, Servo
import time
s1 = ContinuousServo('d1', channel = 13, stop_value = 0.03, forward = 0.08, backward = 0)
d1_fwd = Switch('door_1_fwd', 27, target_on = s1.forward, target_off=s1.disable)
while True:
    time.sleep(0.025)