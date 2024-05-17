import tkinter as tk
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
                  command=self.return_main_page).grid(row=2, column=1)
        
    def create_page(self, main) -> None:
        self.main = main
        self.create_timeline()
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
        t.grid(row=0, column=0, columnspan= 2, sticky="we")
    
    def callback(self, training_id):
        self.frame.grid_forget()
        StatsTimelinePage(training_id, self.db_manager).create_page(self.frame)

class TrainingButton:
    def __init__(self, frame, training : TrainingData, row : int, column : int, db_manager : DatabaseManager) -> None:
        self.db_manager = db_manager
        tk.Button(frame, text=training.training_date, command=lambda : self.change_page(frame, training.training_id)).grid(row=row, column=column, padx=5)

    def change_page(self, frame, training_id : int) -> None:
        frame.grid_forget()
        StatsTimelinePage(training_id, self.db_manager).create_page(frame)
