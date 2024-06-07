from datetime import datetime
import tkinter as tk
import numpy as np
from core.database.DatabaseManager import DatabaseManager,TrainingData
from front.visualization.StatsPage import StatsPage
from front.visualization.StatsTimelinePage import StatsTimelinePage
from front.visualization.TimelineSkater import TimelineSkater

class TrainingPage:
    def __init__(self, trainings : list[TrainingData], skater_id : int, db_manager : DatabaseManager) -> None:
        self.trainings = trainings
        self.skater_id = skater_id
        self.db_manager = db_manager
        self.frame = tk.Frame()
        tk.Button(self.frame, text='Return',
                  command=self.return_main_page).grid(row=5, column=9, columnspan=2, sticky="e")
        
    def create_page(self, main) -> None:
        self.main = main
        self.create_timeline()
        self.create_table()
        self.frame.grid(sticky="we")

    def return_main_page(self) -> None:
        self.frame.grid_forget()
        self.main.grid()

    def create_training_button(self) -> None:
        n = len(self.trainings)
        if n>0:
            sep = n//2 + n%2
            for i,training in enumerate(self.trainings):
                TrainingButton(self.frame, training, i//sep, i%sep, self.db_manager)

    def create_timeline(self) -> None:
        self.frame.grid_columnconfigure(0, weight=1)
        t = TimelineSkater(self.frame, bd=2, relief="groove", background="white", header=self.db_manager.get_skater_name_from_id(self.skater_id), trainings = self.trainings, command=self.callback)
        t.grid(row=0, column=0, columnspan= 11, sticky="we")
    
    def callback(self, training_id):
        self.frame.grid_forget()
        StatsTimelinePage(training_id, self.db_manager).create_page(self.frame)

    def create_table(self) -> tk.Frame:

        self.frame.grid_columnconfigure(0, weight=0)
        for i in range(1,11):
            self.frame.grid_columnconfigure(i, weight=1)

        tk.Label(self.frame, text="").grid(row=2, column=0)

        tk.Label(self.frame, text="Number of jumps").grid(row=3, column=0)
        tk.Label(self.frame, text="% Success").grid(row=4, column=0)

        for i,training in enumerate(self.trainings[-10:]):
            jumps = self.db_manager.load_training_data(training.training_id)
            n_jumps = len(jumps)
            s = 0
            for jump in jumps:
                s += jump.jump_success
            if n_jumps>0:
                perc_success = round(s/n_jumps*100,2)
            else:
                perc_success = 0

            tk.Label(self.frame, text=datetime.fromtimestamp(training.training_date).strftime("%d %b %H:%M")).grid(row=2, column=i+1)
            e = tk.Entry(self.frame)
            e.insert(0, n_jumps)
            e.grid(row=3,column=i+1)
            e = tk.Entry(self.frame)
            e.insert(0, perc_success)
            e.grid(row=4,column=i+1)

        tk.Label(self.frame, text="").grid(row=5, column=0)

class TrainingButton:
    def __init__(self, frame, training : TrainingData, row : int, column : int, db_manager : DatabaseManager) -> None:
        self.db_manager = db_manager
        tk.Button(frame, text=training.training_date, command=lambda : self.change_page(frame, training.training_id)).grid(row=row, column=column, padx=5)

    def change_page(self, frame, training_id : int) -> None:
        frame.grid_forget()
        StatsTimelinePage(training_id, self.db_manager).create_page(frame)
