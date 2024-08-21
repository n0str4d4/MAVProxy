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
    

def init(mpstate):
    return CanSendModule(mpstate)