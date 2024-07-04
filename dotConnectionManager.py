import time
from typing import List
import os
import numpy as np
from core.database.DatabaseManager import DatabaseManager, TrainingData
from xdpchandler import *
import asyncio
if os.name == 'nt':
    from winrt.windows.devices import radios
import threading

from movelladot_pc_sdk.movelladot_pc_sdk_py39_64 import XsDotDevice

async def bluetooth_power(turn_on):
    if os.name == 'nt':
        all_radios = await radios.Radio.get_radios_async()
        for this_radio in all_radios:
            if this_radio.kind == radios.RadioKind.BLUETOOTH:
                if turn_on:
                    result = await this_radio.set_state_async(radios.RadioState.ON)
                else:
                    result = await this_radio.set_state_async(radios.RadioState.OFF)
    else :
        pass
    
class DotConnectionManager:
    def __init__(self):
        self.xdpcHandler = XdpcHandler()
        self.val = 0
        self.usbDevices = []
        self.recordHandler = XdpcHandler()
        if not self.xdpcHandler.initialize():
            self.xdpcHandler.cleanup()
            exit(-1)
        if not self.recordHandler.initialize():
            self.recordHandler.cleanup()
            exit(-1)

    def connectToDots(self):
        asyncio.run(bluetooth_power(True))
        self.resetRecordHandler()
        self.recordHandler.scanForDots()
        maxTry = 0
        while len(self.recordHandler.connectedDots()) < len(self.recordHandler.detectedDots()) and maxTry <= 100:
            self.recordHandler.connectDots()
            maxTry += 1
        for x in self.recordHandler.connectedDots():
            print(x.deviceId())
        dots = []
        for device in self.recordHandler.connectedDots():
            dots.append(device)
        return dots
    
    def resetRecordHandler(self):
        self.recordHandler.cleanup()
        self.recordHandler.resetWaitingConnection()
        self.recordHandler.resetConnectedDots()
        self.recordHandler = XdpcHandler()
        if not self.recordHandler.initialize():
            self.recordHandler.cleanup()
            exit(-1)

    def newStartRecord(self, device : XsDotDevice):
        device.startRecording()

    def startrecord(self, lastDisconnected, skater_id, db_manager : DatabaseManager):
        xdpcHandler = XdpcHandler()
        if not xdpcHandler.initialize():
            xdpcHandler.cleanup()
            exit(-1)
        bluetooth_address = db_manager.get_bluetooth_address(lastDisconnected)
        xdpcHandler.scanOneDots(bluetooth_address)
        while len(xdpcHandler.connectedDots()) != len(xdpcHandler.detectedDots()):
            xdpcHandler.connectOneDot(bluetooth_address)
        for device in xdpcHandler.connectedDots():
            if str(device.deviceId()) in lastDisconnected:
                print("Starting onboard recording")
                device.startRecording()
                new_training = TrainingData(0, skater_id[0].id, 0, str(device.deviceId()))
                db_manager.set_current_record(str(device.deviceId()), db_manager.save_training_data(new_training))
            else : 
                print("Not the correct dot")
        xdpcHandler.cleanup()
        xdpcHandler.resetWaitingConnection()

    def stoprecord(self, lastConnected : List[XsDotDevice], db_manager : DatabaseManager):
        xdpcHandler = XdpcHandler()
        if not xdpcHandler.initialize():
            xdpcHandler.cleanup()
            exit(-1)
        bluetooth_address = db_manager.get_bluetooth_address(lastConnected)
        xdpcHandler.scanOneDots(bluetooth_address)
        while len(xdpcHandler.connectedDots()) != len(xdpcHandler.detectedDots()):
            xdpcHandler.connectOneDot(bluetooth_address)
        for device in xdpcHandler.connectedDots():
            print(device.deviceId())
            if str(device.deviceId()) in lastConnected:
                print("Stoping onboard recording")
                device.stopRecording()
                current_record = db_manager.get_current_record(str(device.deviceId()))
                db_manager.set_training_date(current_record, device.getRecordingInfo(device.recordingCount()).startUTC())
                db_manager.set_current_record(str(device.deviceId()), "0")
            else : 
                print("Not the correct dot")    
        xdpcHandler.cleanup()
        xdpcHandler.resetWaitingConnection()
    
    def detectUsbDots(self):
        self.xdpcHandler.detectUsbDevices()
        if len(self.xdpcHandler.detectedDots())-self.val != 0:
            self.val = len(self.xdpcHandler.detectedDots())
        self.xdpcHandler.resetConnectedDots()
        self.xdpcHandler.cleanup()

    def dotConnection(self):
        lastDisconnected = []
        lastConnected = []
        asyncio.run(bluetooth_power(False))
        self.xdpcHandler.detectUsbDevices()
        if len(self.xdpcHandler.detectedDots())-val != 0:
            if len(self.xdpcHandler.detectedDots())-val == 1:
                print("Connected, extracting data")
                self.xdpcHandler.connectDots()
                connectedUsb = []
                isRecording = False
                for usb in self.xdpcHandler.connectedUsbDots():
                    if not str(usb.deviceId()) in self.usbDevices:
                        lastConnected.append(str(usb.deviceId()))
                    connectedUsb.append(str(usb.deviceId()))
                    isRecording += (usb.recordingCount()==-1)
                self.usbDevices = connectedUsb
                self.xdpcHandler.cleanup()
                if isRecording:
                    asyncio.run(bluetooth_power(True))
                    self.stoprecord(lastConnected)
            elif len(self.xdpcHandler.detectedDots())-val == -1:
                print("Starting recording")
                self.xdpcHandler.connectDots()
                connectedUsb = []
                for x in self.xdpcHandler.connectedUsbDots():
                    connectedUsb.append(str(x.deviceId()))
                for usb in self.usbDevices:
                    if not usb in connectedUsb:
                        lastDisconnected.append(usb)
                self.usbDevices = connectedUsb
                asyncio.run(bluetooth_power(True))
                self.startrecord(lastDisconnected)
            val = len(self.xdpcHandler.detectedDots())
        self.xdpcHandler.resetConnectedDots()
        self.xdpcHandler.cleanup()
