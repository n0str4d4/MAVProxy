#!/usr/bin/env python
'''can send'''

import time, os
from numpy import equal
from pymavlink import mavutil
from math import *


from MAVProxy.modules.lib import mp_module

import tkinter as tk
import threading 

class CanSendModule(mp_module.MPModule):
    def __init__(self,mpstate):
        super(CanSendModule, self).__init__(mpstate,"cansend",public=True)
        self.add_command('cansend', self.send_mavlink_can_msg,"send CAN message over MAVLink")
        self.add_command('canset', self.set_can_channels, "setup local CAN IDs for Throttle/Rudder/Gear - not propagated to CCU")
        # Register to handle incoming CAN_FRAME messages
        
        # self.master.mavlink_callbacks.append(self.handle_can_frame)

        # print(vars(self.master))
        # print(self.master.__dict__)
        # print(help(self.master))
        # self.root = tk.Tk()
        # self.root.title = "CAN Frame Viewer"
        # self.text = tk.Text(self.root, wrap='word', height=20, width=50)
        # self.text.pack()
        # self.root.after(100, self.update_gui)

         
        # Start a dedicated thread for receiving CAN frames
        self.running = True
        self.recv_thread = threading.Thread(target=self.recv_loop)
        self.recv_thread.daemon = False  # Daemonize the thread so it exits when main program exits
        self.recv_thread.start()

        self.throttleCANID = 0
        self.rudderCANID   = 0
        self.gearCANID     = 0


    def recv_loop(self):
        while self.running:
            # Continuously poll for CAN frames without blocking the main thread
            msg = self.master.recv_match(type='CAN_FRAME', blocking=False)
            if msg:
                self.handle_can_frame(msg)

    # def idle_task(self):
    #     # he idle_task method in the MPModule class is a periodic task that 
    #     # can be overridden to check for and handle incoming MAVLink messages.
    #     # This function is called periodically to handle incoming messages
    #     print('from within the idle task')
    #     msg = self.master.recv_match(type='CAN_FRAME', blocking=False)
        
    #     if msg:
    #         self.handle_can_frame(msg)
    
    def send_mavlink_can_msg(self, args): #args):
        can_id = 0
        data = []
        bus = 0
        target_system = 1
        target_component = 1

        '''send can messages through MAVLink'''
        if ( len(args) != 2):
            print("Usage: cansend [RUDDER/THROTTLE/GEAR] [PERCENTAGE/LEVEL]")
            return
        
        if ( len(args) == 2):
            if(args[0] == 'THROTTLE'):
                if (int(args[1]) < 0 or int(args[1]) > 100):
                    print("Usage: cansend THROTTLE [0:100]")
                    
                elif self.throttleCANID == 0:
                    print("Setup CANIDs Using canset command")
                    
                else:
                    data = self.decimal_to_padded_hex_array(int(args[1]), 'THROTTLE') 
                    can_id = self.throttleCANID  

            if(args[0] == 'RUDDER'):
                if (int(args[1]) < -90 or int(args[1]) > 90):
                    print("Usage: cansend RUDDER [-90:90]")
                    
                elif self.rudderCANID == 0:
                    print("Setup CANIDs Using canset command")
                    
                else:
                    data = self.decimal_to_padded_hex_array(int(args[1]), 'RUDDER') 
                    can_id = self.rudderCANID  

            if(args[0] == 'GEAR'):
                # if (int(args[1]) not in ('F','R','N')): #or int(args[1]) > 100):
                #     print("Usage: cansend GEAR F/N/R")
                    
                # elif self.gearCANID == 0:
                #     print("Setup CANIDs Using canset command")
                    
                # else:
                #     data = self.decimal_to_padded_hex_array(int(ord(str(args[1])),10), 'GEAR') 
                #     can_id = self.gearCANID  
                gear = args[1].upper()
                if gear not in ('F', 'R', 'N'):
                    print("Usage: cansend GEAR F/N/R")
                elif self.gearCANID == 0:
                    print("Setup CANIDs Using canset command")
                else:
                    gear_map = {'F': 70, 'R': 82, 'N': 78}
                    data = self.decimal_to_padded_hex_array(gear_map[gear], 'GEAR')
                    can_id = self.gearCANID


            

        if(can_id != 0): 

        # can_id = 0x999
        # data = ['0x01', '0x02', '0x03', '0x04', '0x05', '0x06', '0x07', '0x08']

        # data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
        # can_id = 0x99
            bus = 0
    
    # Send the CAN frame
            self.master.mav.can_frame_send(
                len=len(data),
                bus=bus,
                id=can_id,
                data=data,
                target_system=target_system,
                target_component=target_component
            )
            print(f"Sent CAN frame with ID {can_id:#x} on bus {bus} with data {data}")
            # self.text.insert(tk.END, f"Sent CAN frame: ID={can_id:#x}, Bus={bus}, Data={data}\n")

    
    def handle_can_frame(self, m):
        print(f"the MAVLink message received is of type {m.get_type()}")
        # This function is called when a CAN_FRAME message is received
        if m.get_type() == 'CAN_FRAME':
            can_id = m.id
            bus = m.bus
            data = list(m.data)
            print(f"Received CAN frame: ID={can_id:#x}, Bus={bus}, Data={data}")
            # self.text.insert(tk.END, f"Received CAN frame: ID={can_id:#x}, Bus={bus}, Data={data}\n")

     
    def unload(self):
        # Ensure the thread is stopped when the module is unloaded
        self.running = False
        self.recv_thread.join()

    def set_can_channels(self,args):
        if ( len(args) != 2):
            print("Usage: canset [THROTTLE/RUDDER/GEAR] CANID_IN_DEC")
            return
        if ( len(args) == 2):
            if(args[0] == 'THROTTLE'):
                self.throttleCANID = int(args[1])
                print(self.throttleCANID)
            elif (args[0] == 'RUDDER'):
                self.rudderCANID = int(args[1])
            elif (args[0] == 'GEAR'):
                self.gearCANID = int(args[1])
            else: 
                print("Usage: canset [THROTTLE/RUDDER/GEAR] CANID")
                return
        
    def decimal_to_padded_hex_array(self,decimal_number,targetComponent):

        # abs_dec = abs(decimal_number)
        #  # Convert the decimal number to a hexadecimal string (without the '0x' prefix)
        # hex_string = hex(abs_dec)[2:].upper()
        #  # Fill in the array of 8 bytes with 0x00, except the LSB with actual data 
        # hex_array = []

        # if(targetComponent == 'RUDDER'):
        #     # L	Set the DATA MSB to 11 
        #     # R	Set the DATA MSB to 00
        #     if(decimal_number > 0):
        #         hex_array.append(int('0x11',16))
                
        #     else:
        #         hex_array.append(int('0x00',16))

        #  # range from 0 to 7 for a DATA of 8 bytes
        # for i in range(7):
        #     if( i == 6):
        #         hex_array.append(int(hex_string,16))
        #     else:
        #         hex_array.append(int('0x00',16))
        
         # Check for target component to set the DATA MSB accordingly 
        
                
            # Convert the decimal number to a hexadecimal string (without the '0x' prefix)
            # hex_string = hex(decimal_number)[2:].upper()   
            
            # Pad the hex string to ensure it has at least 8 characters
            # hex_string = hex_string.zfill(8)
            
            # Create a list of integers representing each hex digit with 0x prefix
            #hex_array = [int(f'0x{digit}', 16) for digit in hex_string]
            
                
        # return hex_array

        abs_dec = abs(decimal_number)
        
        # Convert the decimal number to a hexadecimal string (without the '0x' prefix)
        hex_string = hex(abs_dec)[2:].upper().zfill(2)  # Ensure at least 2 characters for the smallest hex value
        
        # Initialize the hex_array with 0x00 values
        hex_array = [0x00] * 8

        # Set the MSB based on targetComponent and decimal_number
        if targetComponent == 'RUDDER':
            # Set the DATA MSB based on the sign of decimal_number
            hex_array[0] = 0xFF if decimal_number < 0 else 0x00
            # Ensure the last element of hex_array is set with actual data
            hex_array[7] = int(hex_string,16)

        elif targetComponent == 'THROTTLE':
            #hex_array[0] = 0x00
            # Ensure the last element of hex_array is set with actual data
            hex_array[7] = int(hex_string,16)

        elif targetComponent == 'GEAR':
            # #hex_array[0] = 0x00
            # # denoting FORWARD F
            # if(abs_dec == 70): hex_array[7] = int('0x01',16)
            # # denoting REVERSE R
            # if(abs_dec == 82): hex_array[7] = int('0x02',16)
            # # denoting NEUTRAL N
            # if(abs_dec == 78): hex_array[7] = int('0x03',16)
            gear_map = {70: 0x01, 82: 0x02, 78: 0x03}
            if abs_dec in gear_map:
                hex_array[7] = gear_map[abs_dec]
            
        
        # Ensure the last element of hex_array is set with actual data
        #hex_array[7] = int(hex_string,16)
        
        return hex_array

        

        
    # def update_gui(self):
    #     self.root.update_idletasks()
    #     self.root.update()
    #     self.root.after(100, self.update_gui)


def init(mpstate):
    return CanSendModule(mpstate)