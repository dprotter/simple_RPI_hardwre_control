from components import Switch, SwitchManager, Box, ContinuousServo, Servo, print_pin_status
switch_manager = SwitchManager()
s1 = ContinuousServo('d1', channel = 13, stop_value = 0.03, forward = 0.08, backward = 0)
d1_fwd = switch_manager.new_switch('door_1_fwd', 27, target_on = s1.forward, target_off=s1.disable)



import time
try:
    while True:
        print_pin_status(switch_manager.switches)
        time.sleep(0.05)

except KeyboardInterrupt:
    pass