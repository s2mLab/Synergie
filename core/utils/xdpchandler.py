
#  Copyright (c) 2003-2023 Movella Technologies B.V. or subsidiaries worldwide.
#  All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without modification,
#  are permitted provided that the following conditions are met:
#  
#  1.	Redistributions of source code must retain the above copyright notice,
#  	this list of conditions and the following disclaimer.
#  
#  2.	Redistributions in binary form must reproduce the above copyright notice,
#  	this list of conditions and the following disclaimer in the documentation
#  	and/or other materials provided with the distribution.
#  
#  3.	Neither the names of the copyright holders nor the names of their contributors
#  	may be used to endorse or promote products derived from this software without
#  	specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
#  EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
#  THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
#  OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY OR
#  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  

from typing import List
import movelladot_pc_sdk
from user_settings import *
import time

from movelladot_pc_sdk.movelladot_pc_sdk_py39_64 import XsPortInfo, XsDotDevice, XsDotUsbDevice, XsDotConnectionManager

waitForConnections = True

def on_press(key):
    global waitForConnections
    waitForConnections = False

class XdpcHandler(movelladot_pc_sdk.XsDotCallback):
    def __init__(self):
        movelladot_pc_sdk.XsDotCallback.__init__(self)

        self.__manager : XsDotConnectionManager = 0
        self.__errorReceived = False
        self.__updateDone = False
        self.__detectedDots = list()
        self.__connectedDots = list()
        self.__connectedUsbDots = list()

    def initialize(self):
        """
        Initialize the PC SDK

        - Prints the used PC SDK version to show we connected to XDPC
        - Constructs the connection manager used for discovering and connecting to DOTs
        - Connects this class as callback handler to the XDPC

        Returns:
            False if there was a problem creating a connection manager.
        """
        # Create connection manager
        self.__manager = movelladot_pc_sdk.XsDotConnectionManager()
        if self.__manager is None:
            print("Manager could not be constructed, exiting.")
            return False

        # Attach callback handler (self) to connection manager
        self.__manager.addXsDotCallbackHandler(self)
        return True

    def cleanup(self):
        """
        Close connections to any Movella DOT devices and destructs the connection manager created in initialize
        """
        self.__manager.close()

    def scanForDots(self):
        """
        Scan if any Movella DOT devices can be detected via Bluetooth

        Enables device detection in the connection manager and uses the
        onAdvertisementFound callback to detect active Movella DOT devices
        Disables device detection when done

        """
        # Start a scan and wait until we have found one or more DOT Devices
        print("Scanning for devices...")
        self.__manager.enableDeviceDetection()

        print("Press any key or wait 10 seconds to stop scanning...")
        connectedDOTCount = 0
        startTime = movelladot_pc_sdk.XsTimeStamp_nowMs()
        while waitForConnections and not self.errorReceived() and movelladot_pc_sdk.XsTimeStamp_nowMs() - startTime <= 10000:
            time.sleep(0.1)

            nextCount = len(self.detectedDots())
            if nextCount != connectedDOTCount:
                print(f"Number of connected DOTs: {nextCount}. Press any key to start.")
                connectedDOTCount = nextCount

        self.__manager.disableDeviceDetection()
        print("Stopped scanning for devices.")

    def connectDots(self):
        """
        Connects to Movella DOTs found via either USB or Bluetooth connection

        Uses the isBluetooth function of the XsPortInfo to determine if the device was detected
        via Bluetooth or via USB. Then connects to the device accordingly
        When using Bluetooth, a retry has been built in, since wireless connection sometimes just fails the 1st time
        Connected devices can be retrieved using either connectedDots() or connectedUsbDots()

        USB and Bluetooth devices should not be mixed in the same session!
        """
        for portInfo in self.detectedDots():
            if portInfo.isBluetooth():
                address = portInfo.bluetoothAddress()

                checkDevice = False

                while not checkDevice:
                    if not self.__manager.openPort(portInfo):
                        print(f"Connection to Device {address} failed")
                        checkDevice = False
                    else:
                        device : XsDotDevice = self.__manager.device(portInfo.deviceId())
                        if device is None:
                            checkDevice = False

                        devicesId = []
                        for x in self.__connectedDots:
                            devicesId.append(x.deviceId())

                        checkDevice = (device.deviceId() not in devicesId) and (device.deviceTagName() != '')

                self.__connectedDots.append(device)
                print(f"Found a device with Tag: {device.deviceTagName()} @ address: {address}")
            else:
                print(f"Opening DOT with ID: {portInfo.deviceId().toXsString()} @ port: {portInfo.portName()}, baudrate: {portInfo.baudrate()}")
                if not self.__manager.openPort(portInfo):
                    print(f"Could not open DOT. Reason: {self.__manager.lastResultText()}")
                    continue

                device = self.__manager.usbDevice(portInfo.deviceId())
                if device is None:
                    continue

                self.__connectedUsbDots.append(device)
                print(f"Device: {device.productCode()}, with ID: {device.deviceId().toXsString()} opened.")

    def detectUsbDevices(self):
        """
        Scans for USB connected Movella DOT devices for data export
        """
        self.__detectedDots = self.__manager.detectUsbDevices()

    def detectedDots(self) -> List[XsPortInfo]:
        """
        Returns:
             An XsPortInfoArray containing information on detected Movella DOT devices
        """
        return self.__detectedDots

    def connectedDots(self)-> List[XsDotDevice]:
        """
        Returns:
            A list containing an XsDotDevice pointer for each Movella DOT device connected via Bluetooth
        """
        return self.__connectedDots

    def connectedUsbDots(self) -> List[XsDotUsbDevice]:
        """
        Returns:
             A list containing an XsDotUsbDevice pointer for each Movella DOT device connected via USB */
        """
        return self.__connectedUsbDots

    def errorReceived(self):
        """
        Returns:
             True if an error was received through the onError callback
        """
        return self.__errorReceived

    def updateDone(self):
        """
        Returns:
             Whether update done was received through the onDeviceUpdateDone callback
        """
        return self.__updateDone

    def resetUpdateDone(self):
        """
        Resets the update done member variable to be ready for a next device update
        """
        self.__updateDone = False

    def onAdvertisementFound(self, port_info):
        """
        Called when an Movella DOT device advertisement was received. Updates m_detectedDots.
        Parameters:
            port_info: The XsPortInfo of the discovered information
        """
        if not whitelist or port_info.bluetoothAddress() in whitelist:
            self.__detectedDots.append(port_info)
        else:
            print(f"Ignoring {port_info.bluetoothAddress()}")

    def onError(self, result, errorString):
        """
        Called when an internal error has occurred. Prints to screen.
        Parameters:
            result: The XsResultValue related to this error
            errorString: The error string with information on the problem that occurred
        """
        print(f"{movelladot_pc_sdk.XsResultValueToString(result)}")
        print(f"Error received: {errorString}")
        self.__errorReceived = True

    def onDeviceUpdateDone(self, portInfo, result):
        """
        Called when the firmware update process has completed. Prints to screen.
        Parameters:
            portInfo: The XsPortInfo of the updated device
            result: The XsDotFirmwareUpdateResult of the firmware update
        """
        print(f"\n{portInfo.bluetoothAddress()}  Firmware Update done. Result: {movelladot_pc_sdk.XsDotFirmwareUpdateResultToString(result)}")
        self.__updateDone = True
