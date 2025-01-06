from datetime import datetime
import os
import sys
from threading import Event
import time
from movelladot_pc_sdk.movelladot_pc_sdk_py39_64 import XsDotDevice, XsDotUsbDevice, XsDotConnectionManager, XsDotCallback, XsPortInfo, XsDataPacket
import movelladot_pc_sdk
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageTk
from constants import *

from core.database.DatabaseManager import DatabaseManager, JumpData

class DotDevice(XsDotCallback):
    """
    Class permettant de gérer individuellement les capteurs, elle remplace les classes fournis par movella_pc_sdk :
    XsDotDevice : capteur connecté en bluetooth
    XsDotUsbDevice : capteur connecté en USB
    Les deux classes sont fusionnéees dans celle-ci.
    La classe est une extension de XsDotCallback qui permet d'avoir des retours des capteurs
    """
    def __init__(self, portInfoUsb : XsPortInfo, portInfoBt : XsPortInfo, db_manager : DatabaseManager):
        XsDotCallback.__init__(self)
        self.portInfoUsb = portInfoUsb
        self.portInfoBt = portInfoBt
        self.db_manager = db_manager

        self.usbManager = XsDotConnectionManager()
        while self.usbManager is None:
            self.usbManager = XsDotConnectionManager()
        self.usbManager.addXsDotCallbackHandler(self)

        self.btManager = XsDotConnectionManager()
        while self.btManager is None:
            self.btManager = XsDotConnectionManager()
        self.btManager.addXsDotCallbackHandler(self)

        self.usbDevice : XsDotUsbDevice = None
        self.btDevice : XsDotDevice = None
        self.initializeUsb()
        self.initializeBt()
        self.deviceId = str(self.usbDevice.deviceId())
        self.deviceTagName = str(self.btDevice.deviceTagName())
        self.batteryLevel = self.btDevice.batteryLevel()
        self.isRecording = self.usbDevice.recordingCount() == -1
        if self.isRecording:
            self.recordingCount = 0
        else:
            self.recordingCount = self.usbDevice.recordingCount()
        self.isPlugged = True
        self.timingRecord = datetime.now().timestamp()

        self.loadImages()
        self.currentImage = self.imageActive

        self.count = 0
        self.packetsReceived = []
        self.synchroTime = 0
        self.exportDone = False

    def initializeBt(self):
        """
        Initialise la connexion bluetooth
        """
        self.btManager.closePort(self.portInfoBt)
        checkDevice = False
        while not checkDevice:
            self.btManager.closePort(self.portInfoBt)
            if not self.btManager.openPort(self.portInfoBt):
                print(f"Connection to Device {self.portInfoBt.bluetoothAddress()} failed")
                checkDevice = False
            else:
                device : XsDotDevice = self.btManager.device(self.portInfoBt.deviceId())
                if device is None:
                    checkDevice = False
                else:
                    time.sleep(1)
                    checkDevice = (device.deviceTagName() != '') and (device.batteryLevel() != 0)
        self.btDevice = device

    def initializeUsb(self):
        """
        Initialise la connexion USB
        """
        self.usbManager.closePort(self.portInfoUsb)
        device = None
        while device is None:
            self.usbManager.openPort(self.portInfoUsb)
            device = self.usbManager.usbDevice(self.portInfoUsb.deviceId())
        self.usbDevice = device
    
    def loadImages(self):
        """
        Charge les images des capteurs pour l'interface graphique
        """
        fontTag = ImageFont.truetype(font="arialbd.ttf",size=60)
        try:
            imgActive = Image.open(f"{sys._MEIPASS}/img/Dot_active.png")
        except:
            imgActive = Image.open(f"img/Dot_active.png")
        d = ImageDraw.Draw(imgActive)
        text = self.deviceTagName
        x = 0
        if len(text) == 1:
            x = 93
        else:
            x = 75
        d.text( (x,65), text,font=fontTag, fill="black")
        imgActive = imgActive.resize((116, 139))
        self.imageActive = ImageTk.PhotoImage(imgActive)

        try:
            imgInactive = Image.open(f"{sys._MEIPASS}/img/Dot_inactive.png")
        except:
            imgInactive = Image.open(f"img/Dot_inactive.png")
        d = ImageDraw.Draw(imgInactive)
        d.text( (x,65), text,font=fontTag, fill="black")
        imgInactive = imgInactive.resize((116, 139))
        self.imageInactive = ImageTk.PhotoImage(imgInactive)
    
    def startRecord(self):
        """
        Commence un enregistrement sur le capteur
        """
        self.isRecording = True
        if not self.btDevice.startRecording():
            self.initializeBt()
            self.isRecording = self.btDevice.startRecording()
        if self.isRecording:
            self.timingRecord = datetime.now().timestamp()
        return self.isRecording

    def stopRecord(self):
        """
        Arrête un enregistrement sur le capteur
        """
        self.isRecording = False
        if not self.btDevice.stopRecording():
            self.initializeBt()
            self.isRecording = not self.btDevice.stopRecording()
        self.recordingCount = self.usbDevice.recordingCount()
        return not self.isRecording

    def exportData(self, saveFile : bool, extractEvent : Event):
        """
        Export les données du capteurs
        saveFile : définis si on veut extraire toute les infos disponibles (et non seulement celle nécessaire aux modèles)
        extractEvent : event pour informer le thread principale que l'extraction est finie
        """
        self.saveFile = saveFile
        print("Exporting...")
        self.exportDone = False
        self.packetsReceived = []
        self.count = 0
        exportData = movelladot_pc_sdk.XsIntArray()
        exportData.push_back(movelladot_pc_sdk.RecordingData_Timestamp)
        exportData.push_back(movelladot_pc_sdk.RecordingData_Euler)
        exportData.push_back(movelladot_pc_sdk.RecordingData_Acceleration)
        exportData.push_back(movelladot_pc_sdk.RecordingData_AngularVelocity)
        if self.saveFile:
            exportData.push_back(movelladot_pc_sdk.RecordingData_MagneticField)
            exportData.push_back(movelladot_pc_sdk.RecordingData_Quaternion)
            exportData.push_back(movelladot_pc_sdk.RecordingData_Status)

        if not self.usbDevice.selectExportData(exportData):
            print(f'Could not select export data. Reason: {self.usbDevice.lastResultText()}')

        for recordingIndex in range(1, self.usbDevice.recordingCount()+1):
            recInfo = self.usbDevice.getRecordingInfo(recordingIndex)
            if recInfo.empty():
                print(f'Could not get recording info. Reason: {self.usbDevice.lastResultText()}')

            dateRecord = recInfo.startUTC()
            trainingId = self.db_manager.get_current_record(self.deviceId)
            if trainingId != "":
                self.db_manager.set_training_date(trainingId, dateRecord)
                if not self.usbDevice.startExportRecording(recordingIndex):
                    print(f'Could not export recording. Reason: {self.usbDevice.lastResultText()}')
                else:
                    while not self.exportDone:
                        time.sleep(0.1)
                    print('File export finished!')
                    if self.saveFile:
                        columnSelected = ["PacketCounter","SampleTimeFine","Euler_X","Euler_Y","Euler_Z","Quat_W","Quat_X","Quat_Y","Quat_Z","Acc_X","Acc_Y","Acc_Z","Gyr_X","Gyr_Y","Gyr_Z","Mag_X","Mag_Y","Mag_Z"]
                    else:
                        columnSelected = ["PacketCounter","SampleTimeFine","Euler_X","Euler_Y","Euler_Z","Acc_X","Acc_Y","Acc_Z","Gyr_X","Gyr_Y","Gyr_Z"]
                    df = pd.DataFrame.from_records(self.packetsReceived, columns=columnSelected)
                    date = datetime.fromtimestamp(dateRecord).strftime("%Y_%m_%d")
                    startSampleTime = df["SampleTimeFine"][0]
                    newSampleTimeFine = []
                    for timeFine in df["SampleTimeFine"]:
                        newTime = timeFine - startSampleTime
                        if newTime < 0:
                            newSampleTimeFine.append(newTime + 2**32)
                        else:
                            newSampleTimeFine.append(newTime)
                    df["SampleTimeFine"] = newSampleTimeFine
                    self.synchroTime = max(0, self.synchroTime - startSampleTime)
                    os.makedirs(f"data/raw/{date}", exist_ok = True)
                    df.to_csv(f"data/raw/{date}/{self.synchroTime}_{trainingId}.csv", index=False)

                    self.predict_training(trainingId, df)
                    self.db_manager.remove_current_record(self.deviceId, trainingId)
                    self.recordingCount -= 1
        
        self.usbDevice.eraseFlash()
        print("You can disconnect the dot")
        self.recordingCount = 0
        extractEvent.set()
        self.currentImage = self.imageActive

    def predict_training(self, training_id : str, df : pd.DataFrame):
        from core.data_treatment.data_generation.exporter import export
        """
        Utilisation des modèles de prédiction pour avoir les infos de l'enregistrement
        """
        try:
            df = export(df)
            print("End of process")
            trainingJumps = []
            unknow_rotation = []
            for iter,row in df.iterrows():
                jump_time_min, jump_time_sec = row["videoTimeStamp"].split(":")
                jump_time = '{:02d}:{:02d}'.format(int(jump_time_min), int(jump_time_sec))
                val_rot = float(row["rotations"])
                if row["type"] < 5 and val_rot > 0.5:
                    if val_rot < 2:
                        val_rot = np.ceil(val_rot-0.3)
                    else:
                        val_rot = np.ceil(val_rot-0.15)
                    jump_data = JumpData(0, training_id, jumpType(int(row["type"])).name, val_rot, bool(row["success"]), jump_time, float(row["rotation_speed"]), float(row["length"]))
                    trainingJumps.append(jump_data.to_dict())
                elif row["type"] == 5 and val_rot > 0.8: 
                    val_rot = np.ceil(val_rot-0.7)+0.5
                    jump_data = JumpData(0, training_id, jumpType(int(row["type"])).name, val_rot, bool(row["success"]), jump_time, float(row["rotation_speed"]), float(row["length"]))
                    trainingJumps.append(jump_data.to_dict())
                else:
                    jump_data = JumpData(0, training_id, jumpType(int(row["type"])).name, 0, bool(row["success"]), jump_time, float(row["rotation_speed"]), float(row["length"]))
                    unknow_rotation.append(jump_data)
            if trainingJumps != []:
                self.db_manager.add_jumps_to_training(training_id, trainingJumps)
            else:
                for jump in unknow_rotation:
                    trainingJumps.append(jump.to_dict())
                self.db_manager.add_jumps_to_training(training_id, trainingJumps)
        except:
            pass
        
    def onRecordedDataAvailable(self, device, packet : XsDataPacket):
        """
        Lorsque le capteur est en train d'exporter les données, cette fonction permet de capter les informations renvoyées
        """
        self.count += 1
        euler = packet.orientationEuler()
        captor = packet.calibratedData()
        if self.saveFile:
            quaternion = packet.orientationQuaternion()
            data = np.concatenate([[int(self.count), packet.sampleTimeFine(), euler.x(), euler.y(), euler.z()], quaternion, captor.m_acc, captor.m_gyr, captor.m_mag])
        else:
            data = np.concatenate([[int(self.count), packet.sampleTimeFine(), euler.x(), euler.y(), euler.z()], captor.m_acc, captor.m_gyr])
        self.packetsReceived.append(data)
    
    def onRecordedDataDone(self, device):
        """
        Fonction qui s'active lorsque le capteur a fini d'extraire les données
        """
        self.exportDone = True
    
    def __eq__(self, device) -> bool:
        return (self.usbDevice == device.usbDevice) and (self.btDevice == device.btDevice)
    
    def getExportEstimatedTime(self) -> int:
        """
        Calcul une estimation du temps d'extraction
        """
        estimatedTime = 0
        for index in range(1,self.usbDevice.recordingCount()+1):
            estimatedTime = estimatedTime + round(self.usbDevice.getRecordingInfo(index).storageSize()/(237568*8),1)
        return estimatedTime + 1

    def onBatteryUpdated(self, device: XsDotDevice, batteryLevel: int, chargingStatus: int):
        self.batteryLevel = batteryLevel
    
    def onButtonClicked(self, device: XsDotDevice, timestamp : int):
        """
        Appuyer sur le bouton pendant l'enregistrement stocke l'instant pour pouvoir synchroniser avec une vidéo lors des collectes de données
        """
        self.synchroTime = timestamp

    def closeUsb(self):
        """
        Ferme la connexion USB
        """
        self.usbManager.closePort(self.portInfoUsb)
        self.isPlugged = False
    
    def openUsb(self):
        """
        Ouvre la connexion USB
        """
        device = None
        while device is None:
            self.usbManager.openPort(self.portInfoUsb)
            device = self.usbManager.usbDevice(self.portInfoUsb.deviceId())
        self.usbDevice = device
        self.isPlugged = True
