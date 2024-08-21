#!/usr/bin/env python
'''can send'''

import time, os
from numpy import equal
from pymavlink import mavutil
from math import *

from MAVProxy.modules.lib import mp_module

class CanSendModule(mp_module.MPModule):
    def __init__(self,mpstate):
        super(CanSendModule, self).__init__(mpstate,"cansend",public=True)
        self.add_command('cansend', self.send_mavlink_can_msg,"send CAN message over MAVLink")
        # Register to handle incoming CAN_FRAME messages
        
        # self.master.mavlink_callbacks.append(self.handle_can_frame)

        # print(vars(self.master))
        # print(self.master.__dict__)
        # print(help(self.master))


    def idle_task(self):
        # he idle_task method in the MPModule class is a periodic task that 
        # can be overridden to check for and handle incoming MAVLink messages.
        # This function is called periodically to handle incoming messages
        #print('from within the idle task')
        msg = self.master.recv_match(type='CAN_FRAME', blocking=True)
        if msg:
            self.handle_can_frame(msg)
    
    def send_mavlink_can_msg(self, args): #args):
        '''send can messages through MAVLink'''
        # if ( len(args) != 2):
        #     print("Usage: cansend 11_BYTE_CAN_ID 8_BYTE_CAN_MESSAGE")
        #     return
        
        # if ( len(args) == 2):
        #     self.master.mav.com
        can_id = 0x999
        data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
        bus = 0
        
        # Send the CAN frame
        self.master.mav.can_frame_send(
            len=len(data),
            bus=bus,
            id=can_id,
            data=data,
            target_system=1,
            target_component=1
        )
        print(f"Sent CAN frame with ID {can_id:#x} on bus {bus} with data {data}")
    
    def handle_can_frame(self, m):
        print(f"the MAVLink message received is of type {m.get_type()}")
        # This function is called when a CAN_FRAME message is received
        if m.get_type() == 'CAN_FRAME':
            can_id = m.id
            bus = m.bus
            data = list(m.data)
            print(f"Received CAN frame: ID={can_id:#x}, Bus={bus}, Data={data}")
     

def init(mpstate):
    return CanSendModule(mpstate)