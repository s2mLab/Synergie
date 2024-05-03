import time
import tkinter as tk
import threading
import os

import pandas as pd

from core.data_treatment.data_generation.exporter import export
from core.database.DatabaseManager import *
from front.DevPage import DevPage
from front.MainPage import MainPage

class App:
    def __init__(self, master):
        self.db_manager = DatabaseManager()
        MainPage(self.db_manager, master)
        #DevPage(master)
        detection_thread = threading.Thread(target=self.run, args=())
        detection_thread.daemon = True
        detection_thread.start()

    def run(self):
        while True :
            list_file = os.listdir("data/new/")
            if len(list_file)>0:
                file = os.path.join("data/new/", list_file[0])
                new_file = os.path.join("data/processing/", list_file[0])
                os.replace(file, new_file)
                self.export_thread(new_file)
            time.sleep(1)
        
    def export_thread(self, path):
        self.path = path
        print("Processing")
        process_thread = threading.Thread(target=self.export_file, args=())
        process_thread.daemon = True
        process_thread.start()
    
    def export_file(self):
        skater_id, df = export(self.path)
        print("End of process")
        os.remove(self.path)
        training_id = self.db_manager.save_training_data(TrainingData(0, skater_id, datetime.now()))
        for iter,row in df.iterrows():
            jump_time_min, jump_time_sec = row["videoTimeStamp"].split(":")
            jump_time = int(jump_time_min)*60 + int(jump_time_sec)
            jump_data = JumpData(0, training_id, int(row["type"]), bool(row["success"]), jump_time)
            self.db_manager.save_jump_data(jump_data)


root = tk.Tk()
myapp = App(root)
root.geometry("1000x400")
root.mainloop()