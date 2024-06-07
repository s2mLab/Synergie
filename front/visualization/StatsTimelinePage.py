import tkinter as tk

import constants
from core.database.DatabaseManager import DatabaseManager
from core.data_treatment.DataCollector import *
from front.visualization.TimelineTraining import TimelineTraining

class StatsTimelinePage():
    def __init__(self, training : int, db_manager : DatabaseManager) -> None:
        self.frame = tk.Frame()
        self.training = training
        tk.Button(self.frame, text='Return',
                  command=self.return_training_page).grid(row=11, column=11, columnspan=2, sticky="e")
        self.data = db_manager.load_training_data(training)
        self.frame.grid_columnconfigure(0, weight=0)
        self.frame.grid_columnconfigure(1, weight=1)
        self.entry_type = tk.Entry(self.frame)
        self.entry_rotations = tk.Entry(self.frame)
        self.entry_success = tk.Entry(self.frame)
        tk.Label(self.frame, text="Type :").grid(row=1,column=0, columnspan=6, sticky="e")
        tk.Label(self.frame, text="Rotations :").grid(row=2,column=0, columnspan=6, sticky="e")
        tk.Label(self.frame, text="Success :").grid(row=3,column=0, columnspan=6, sticky="e")
        for i,e in enumerate([self.entry_type, self.entry_rotations, self.entry_success]):
            e.grid(row=i+1, column=6, columnspan=7, sticky="w")

    def create_page(self, main) -> None:
        self.main = main
        self.create_timeline()
        self.create_table()
        self.frame.grid(sticky="we")

    def return_training_page(self) -> None:
        self.frame.grid_forget()
        self.main.grid(sticky="we")

    def create_timeline(self) -> None:
        self.frame.grid_columnconfigure(0, weight=1)
        t = TimelineTraining(self.frame, bd=2, relief="groove", background="white", jumps = self.data, command=self.callback)
        t.grid(row=0, column=0, columnspan=14, sticky="we")
        
    def callback(self, type, rotations, success):
        self.entry_type.delete(0,'end')
        self.entry_type.insert(0,constants.jumpType(type).name)
        self.entry_rotations.delete(0,'end')
        self.entry_rotations.insert(0,rotations)
        self.entry_success.delete(0,'end')
        self.entry_success.insert(0,constants.jumpSuccess(success).name)

    def create_table(self) -> tk.Frame:

        
        self.frame.grid_columnconfigure(0, weight=0)
        for i in range(1,14):
            self.frame.grid_columnconfigure(i, weight=1)

        tk.Label(self.frame, text="").grid(row=4, column=0)

        tk.Label(self.frame, text="Triple").grid(row=7, column=0)
        tk.Label(self.frame, text="Double").grid(row=8, column=0)
        tk.Label(self.frame, text="Simple").grid(row=9, column=0)

        show_data = np.zeros((6,3,2))

        for jump in self.data:
            rot = int(jump.jump_rotations)
            if rot > 0 and rot < 4:
                show_data[jump.jump_type, rot-1, 1-jump.jump_success] = show_data[jump.jump_type, rot-1, 1-jump.jump_success] + 1

        for i in range(6):
            tk.Label(self.frame, text=constants.jumpType(i).name).grid(row=5, column=2*i+1, columnspan=2)
            tk.Label(self.frame, text="Success").grid(row=6, column=2*i+1)
            tk.Label(self.frame, text="Failure").grid(row=6, column=2*i+2)
            e = tk.Entry(self.frame)
            e.insert(0, int(show_data[i,2,0]))
            e.grid(row=7,column=2*i+1)
            e = tk.Entry(self.frame)
            e.insert(0, int(show_data[i,1,0]))
            e.grid(row=8,column=2*i+1)
            e = tk.Entry(self.frame)
            e.insert(0, int(show_data[i,0,0]))
            e.grid(row=9,column=2*i+1)
            e = tk.Entry(self.frame)
            e.insert(0, int(show_data[i,2,1]))
            e.grid(row=7,column=2*i+2)
            e = tk.Entry(self.frame)
            e.insert(0, int(show_data[i,1,1]))
            e.grid(row=8,column=2*i+2)
            e = tk.Entry(self.frame)
            e.insert(0, int(show_data[i,0,1]))
            e.grid(row=9,column=2*i+2)

        tk.Label(self.frame, text="").grid(row=10, column=0)