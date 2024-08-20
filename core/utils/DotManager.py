import os

import numpy as np
from core.utils.DotDevice import DotDevice
from core.database.DatabaseManager import DatabaseManager
from core.utils.xdpchandler import *
import asyncio
if os.name == 'nt':
    from winrt.windows.devices import radios

async def bluetooth_power(turn_on):
    if os.name == 'nt':
        all_radios = await radios.Radio.get_radios_async()
        for this_radio in all_radios:
            if this_radio.kind == radios.RadioKind.BLUETOOTH:
                if turn_on:
                    result = await this_radio.set_state_async(radios.RadioState.ON)
                else:
                    result = await this_radio.set_state_async(radios.RadioState.OFF)
    else:
        pass

class DotManager:
    def __init__(self, db_manager : DatabaseManager) -> None:
        self.db_manager = db_manager
        self.error = False
        self.devices : List[DotDevice] = []
        self.previousConnected : List[DotDevice] = []

    def firstConnection(self) -> tuple[bool, List[str]]:
        check = True
        asyncio.run(bluetooth_power(False))
        xdpcHandler = XdpcHandler()
        if not xdpcHandler.initialize():
            xdpcHandler.cleanup()
        xdpcHandler.detectUsbDevices()
        self.portInfoUsb = {}
        while len(xdpcHandler.connectedUsbDots()) < len(xdpcHandler.detectedDots()):
            xdpcHandler.connectDots()
        for device in xdpcHandler.connectedUsbDots():
            self.portInfoUsb[str(device.deviceId())] = device.portInfo()
        xdpcHandler.cleanup()

        asyncio.run(bluetooth_power(True))
        xdpcHandler = XdpcHandler()
        if not xdpcHandler.initialize():
            xdpcHandler.cleanup()
        xdpcHandler.scanForDots()
        self.portInfoBt = xdpcHandler.detectedDots()
        xdpcHandler.cleanup()

        unconnectedDevice = []

        for portInfoBt in self.portInfoBt:
            device = self.db_manager.get_dot_from_bluetooth(portInfoBt.bluetoothAddress())
            if device is None :
                print("Adding a new device")
                deviceId = self.connectNewDevice(portInfoBt)
            else:
                deviceId = device.id
            portInfoUsb = self.portInfoUsb.get(deviceId, None)
            if portInfoUsb is not None:
                self.devices.append(DotDevice(portInfoUsb, portInfoBt, self.db_manager))
            else:
                print(f"Please plug sensor {device.get('tag_name')}")
                unconnectedDevice.append(device.get('tag_name'))
                time.sleep(5)
                check = False

        self.previousConnected = self.devices
        return (check, unconnectedDevice)
    
    def checkDevices(self) -> tuple[List[DotDevice], List[DotDevice]]:
        connected : List[DotDevice] = []
        for device in self.devices:
            if device.btDevice.isCharging():
                connected.append(device)

        lastConnected = []
        lastDisconnected = []
        if len(self.previousConnected) > len(connected):
            for device in self.previousConnected:
                if device not in connected:
                    device.closeUsb()
                    lastDisconnected.append(device)
        elif len(self.previousConnected) < len(connected):
            for device in connected:
                if device not in self.previousConnected:
                    device.openUsb()
                    lastConnected.append(device)
        else:
            pass

        self.previousConnected = connected
        return(lastConnected,lastDisconnected)

    def getExportEstimatedTime(self):
        estimatedTime = [0]
        for device in self.devices:
            estimatedTime.append(device.getExportEstimatedTime())
        return np.max(estimatedTime)

    def getDevices(self):
        return self.devices
    
    def connectNewDevice(self, portInfoBt : XsPortInfo):
        manager = XsDotConnectionManager()
        checkDevice = False
        while not checkDevice:
            manager.closePort(portInfoBt)
            if not manager.openPort(portInfoBt):
                print(f"Connection to Device {portInfoBt.bluetoothAddress()} failed")
                checkDevice = False
            else:
                device : XsDotDevice = manager.device(portInfoBt.deviceId())
                if device is None:
                    checkDevice = False
                else:
                    time.sleep(1)
                    checkDevice = (device.deviceTagName() != '') and (device.batteryLevel() != 0)
        self.db_manager.save_dot_data(str(device.deviceId()), device.bluetoothAddress(), device.deviceTagName())
        manager.closePort(portInfoBt)
        return str(device.deviceId())
