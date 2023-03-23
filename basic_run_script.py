from components import Switch, SwitchManager, Box, ContinuousServo, Servo


switch_manager = SwitchManager()
s1 = ContinuousServo('door_1s', channel = 13, stop_value = 0.03, forward = 0.08, backward = 0)
d1_fwd = switch_manager.new_switch('door_1_fwd', 1, target_on = s1.forward, target_off=s1.stop )
d1_bck = switch_manager.new_switch('door_1_fwd', 2, target_on = s1.backward, target_off=s1.stop )

s2 = ContinuousServo('door_1', channel = 2, stop_value = 0.03, forward = 0.08, backward = 0)
d1_fwd = switch_manager.new_switch('door_1_fwd', 3, target_on = s2.forward, target_off=s2.stop )
d1_bck = switch_manager.new_switch('door_1_fwd', 4, target_on = s2.backward, target_off=s2.stop )



