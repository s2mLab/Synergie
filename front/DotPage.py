from datetime import datetime
import threading
import queue
import tkinter as tk
import numpy as np

from core.database.DatabaseManager import DatabaseManager, TrainingData
from dotConnectionManager import DotConnectionManager

class DotPage:
    def __init__(self, db_manager : DatabaseManager,  bluetoothEvent : threading.Event) -> None:
        self.db_manager = db_manager
        self.bluetoothEvent = bluetoothEvent
        self.bluetoothEvent.set()
        self.dot_connection_manager = DotConnectionManager()
        self.frame = tk.Frame()

    def create_page(self, main) -> None:
        self.main = main
        tk.Button(self.frame, text='Scan for dots',
                  command=self.make_dot_connection_page).grid(row=0, column=0, columnspan=2)
        tk.Button(self.frame, text='Go to Main Page',
                  command=self.return_main_page).grid(row=10, column=10, sticky="se")
        self.frame.grid()
    
    def return_main_page(self) -> None:
        self.bluetoothEvent.clear()
        self.frame.grid_forget()
        self.main.grid()

    def make_dot_connection_page(self) -> None:
        self.frame.destroy()
        self.frame = tk.Frame()
        self.create_page(self.main)
        dicoDevice = {}
        dotsconnected = self.dot_connection_manager.connectToDots()
        for i,device in enumerate(dotsconnected):
            dicoDevice[str(device.deviceId())] = device.deviceTagName()
            tk.Label(self.frame, text=device.deviceTagName(),).grid(row=1, column=i)
            tk.Label(self.frame, text=f"Battery : {device.batteryLevel()}%").grid(row=2, column=i)
            if device.recordingCount() == -1:
                tk.Label(self.frame, text="Recording On",).grid(row=3, column=i)
            else:
                tk.Label(self.frame, text="Recording Off",).grid(row=3, column=i)
            
            entryvar = tk.StringVar()
            entry = tk.Entry(self.frame, textvariable=entryvar)
            entry.grid(row=4,column=i) 

            StartAndStopButton(self.frame, self.db_manager, device, entry, 5, i)

        self.frame.grid()

    def make_management_page(self) -> None:
        self.frame.grid_forget()

class StartAndStopButton:
    def __init__(self, frame, db_manager : DatabaseManager, device, entry, row : int, column : int) -> None:
        self.db_manager = db_manager
        self.current_record = 0
        tk.Button(frame, text="Start Recording", command=lambda : self.startRecording(device, entry)).grid(row=row, column=column, padx=5)
        tk.Button(frame, text="Stop Recording", command=lambda : self.stopRecording(device)).grid(row=row+1, column=column, padx=5)
    
    def startRecording(self, device, entry):
        skater_id = self.db_manager.get_skater_id_from_name(entry.get())
        if len(skater_id) > 0:
            device.startRecording()
            print(f"{device.deviceTagName()} Recording started for {entry.get()}")
            new_training = TrainingData(0, skater_id[0].id, 0, str(device.deviceId()))
            self.current_record = self.db_manager.save_training_data(new_training)
        else:
            print("Unknown skater")
    
    def stopRecording(self, device):
        device.stopRecording()
        self.db_manager.set_training_date(self.current_record, device.getRecordingInfo(device.recordingCount()).startUTC())
        
    
    