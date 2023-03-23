
import time
import tabulate
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except:
    print('RPi.GPIO not found')
    from .Fake_GPIO import Fake_GPIO
    GPIO = Fake_GPIO()
import inspect
import sys
import threading
try:
    from adafruit_servokit import ServoKit
    SERVO_KIT = ServoKit(channels=16)
except:
    print('adafruit_servokit not found')
    SERVO_KIT = None

def thread_it(func):
        '''simple decorator to pass function to our thread distributor via a queue. 
        these 4 lines took about 4 hours of googling and trial and error.
        the returned 'future' object has some useful features, such as its own task-done monitor. '''
        
        def pass_to_thread(self, *args, **kwargs):
            bound_args = inspect.signature(func).bind(self, *args, **kwargs)
            bound_args.apply_defaults()
            bound_args_dict = bound_args.arguments

            new_kwargs = {k:v for k, v in bound_args_dict.items()}

            thread = threading.Thread(target = func, kwargs = new_kwargs)
            thread.start()
            return thread
        return pass_to_thread

def get_servo(ID, servo_type):
    '''take a servo positional ID on the adafruit board, and the servo type, and return a servo_kit obj'''
    ACCEPTABLE_TYPES = ('positional', 'continuous', 'output')
    if servo_type not in ACCEPTABLE_TYPES:
        raise KeyError(f'servo type was passed as {servo_type}, must be in:\n{ACCEPTABLE_TYPES}')

    if servo_type == 'positional':
        return SERVO_KIT.servo[ID]
    elif servo_type == 'continuous':
        return SERVO_KIT.continuous_servo[ID] 
    else:
        return SERVO_KIT.channel[ID]
    

class Servo:
    def __init__(self, name, channel):
        self.servo = get_servo(channel, servo_type = 'positional')
        self.name = name
    def set_angle(self, angle):
        if angle < 0 or angle >180:
            raise Exception('angle exceeds capabilities for servo')
        else:
            self.servo.angle = angle
    def disable(self):
        self.servo._pwm_out.duty_cycle = 0

class ContinuousServo:
    def __init__(self, name, channel, stop_value = 0, forward = 0.08, backward = 0):
        self.name = name
        self.servo = get_servo(channel, servo_type = 'continuous')
        self.stop_throttle = stop_value
        self.forward_throttle = forward
        self.backward_throttle = backward
    
    def disable(self):
        self.servo._pwm_out.duty_cycle = 0
    
    def stop(self):
        self.servo.throttle = self.stop_throttle
    
    def forward(self):
        self.servo.throttle = self.forward_throttle
    
    def backward(self):
        self.servo.throttle = self.backward_throttle
        
    def shutdown(self):
        self.reset()
    
    def reset(self):
        self.servo.throttle = self.stop_value
        
    def set_throttle(self, throttle):
        self.servo.throttle = throttle

class SwitchManager:
    
    def __init__(self):
        

        self.switches = []
        self.running = True

        self.watch_switches()

    def shutdown(self):
        self.running = False
    
    @thread_it
    def watch_switches(self):
        while self.running:
            for switch in self.switches:
                if GPIO.input(switch.pin) == switch.pressed_val:
                    if not switch.pressed:
                        print(f'{switch.name} pressed')
                    switch.pressed = True
                    if switch.target_on:
                        switch.target_on()
                    
                else:
                    if switch.pressed:
                        if switch.target_off:
                            switch.target_off()
                    switch.pressed = False
            time.sleep(0.005)
    
    def add_switch(self, switch):
        names = [s.name for s in self.switches]
        if switch.name in names:
            pass
        else:
            self.switches.append(switch)
    
    def new_switch(self, name, pin, pu_pd  = 'pullup', target_on = None, target_off = None):
        '''make a new button and add it to the button list'''

        new_button_obj = Switch(name, pin, pu_pd, target_on, target_off)
        new_button_obj.in_switch_manager = True
        self.switches.append(new_button_obj)
        return new_button_obj

class Switch:
    def __init__(self, name, pin, pu_pd = 'pullup', target_on = None, target_off = None):
        self.name = name
        self.pin = pin
        pullup_pulldown = pu_pd
        
        if pullup_pulldown == 'pullup':
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.pressed_val = 0
            
        elif pullup_pulldown == 'pulldown':
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            self.pressed_val = 1
        
        self.pressed = False
        self.target_on = target_on
        self.target_off = target_off
        self.running = False
        self.in_switch_manager = False
        
        #likely could put this in watch_switches
        if target_on or target_off and not self.in_switch_manager:
            self.monitor_for_targets
        
    @thread_it
    def monitor_for_targets(self):
        self.running = True
        while self.running:
            if self.is_pressed():
                self.target_on()
                while self.running and self.is_pressed():
                    '''wait'''
                    time.sleep(0.025)
                if self.target_off:
                    self.target_off()
            time.sleep(0.025)

        
    def shutdown(self):
        self.running = False
        
    def is_pressed(self):
        if self.in_switch_manager:
            return self.pressed
        elif GPIO.input(self.pin) == self.pressed_val:
            return True
        else:
            return False

class Box:
    
    def __init__(self):
        self.components = {}
        
    def add_component(self, component):
        self.components[component.name] = component
    
    def shutdown(self):
        for _, comp in self.components.items():
            comp.shutdown()
    

def print_pin_status(button_list):
    '''takes a list of buttons, starts up threading, and outputs a tab'''
    try:
        num_buttons = len(button_list.buttons)

        print("\033c", end="")
        
        status = []
        for i in range(0,num_buttons,2):
            
            if i+1<num_buttons:
                b1 = button_list.buttons[i]
                b2 = button_list.buttbutton_listons[i+1]
                status += [[b1.name, b1.pressed, b2.name, b2.pressed]]
            else:
                b1 = button_list.buttons[i]
                status += [[b1.name, b1.pressed, '', '']]
        print(tabulate(status, headers = ['button', 'status', 'button', 'status']))
        time.sleep(0.05)
    except KeyboardInterrupt:
        print('exiting tab view')
        

