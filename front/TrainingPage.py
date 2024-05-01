import tkinter as tk
from core.database.DatabaseManager import DatabaseManager,TrainingData
from front.StatsPage import StatsPage

class TrainingPage:
    def __init__(self, trainings : list[TrainingData], db_manager : DatabaseManager):
        self.trainings = trainings
        self.db_manager = db_manager
        self.frame = tk.Frame()
        tk.Label(self.frame, text='Page 1').grid(row=2, column=10)
        tk.Button(self.frame, text='Go to Main Page',
                  command=self.return_main_page).grid(row=2, column=10)
        
    def create_page(self, main):
        self.main = main
        self.create_training_button()
        self.frame.grid()

    def return_main_page(self):
        self.frame.grid_forget()
        self.main.grid()

    def create_training_button(self):
        n = len(self.trainings)
        sep = n//2 + n%2
        for i,training in enumerate(self.trainings):
            TrainingButton(self.frame, training, i//sep, i%sep, self.db_manager)


class TrainingButton:
    def __init__(self, frame, training : TrainingData, row : int, column : int, db_manager : DatabaseManager):
        self.db_manager = db_manager
        tk.Button(frame, text=training.training_date, command=lambda : self.change_page(frame, training.training_id)).grid(row=row, column=column, padx=5)

    def change_page(self, frame, training_id : int):
        frame.grid_forget()
        StatsPage(training_id, self.db_manager).create_page(frame)
