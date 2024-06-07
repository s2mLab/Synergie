import tkinter as tk

from core.database.DatabaseManager import DatabaseManager
from core.data_treatment.DataCollector import *

class StatsPage:
    def __init__(self, training : int, db_manager : DatabaseManager) -> None:
        self.frame = tk.Frame()
        self.training = training
        tk.Button(self.frame, text='Go to Training Page',
                  command=self.return_training_page).grid(row=10, column=10)
        self.data = get_training_session_data(int(self.training), db_manager)

    def create_page(self, main) -> None:
        self.main = main
        self.create_table()
        self.frame.grid()

    def return_training_page(self) -> None:
        self.frame.grid_forget()
        self.main.grid(sticky="we")

    def create_table(self) -> None:
        
        tk.Label(self.frame, text="Success").grid(row=0, column=1)
        tk.Label(self.frame, text="Failure").grid(row=0, column=2)

        for i,name in enumerate(self.data):
            tk.Label(self.frame, text=name).grid(row=i+1,column=0)
            for j in range(2):
                entry = tk.Entry(self.frame)
                entry.insert(j,self.data[name][j])
                entry.grid(row=i+1,column=j+1)
                
        
