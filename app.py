import tkinter as tk

from core.data_treatment.data_generation.exporter import export
from core.database.DatabaseManager import *
from front.DevPage import DevPage
from front.MainPage import MainPage

class App:
    def __init__(self, master):
        self.db_manager = DatabaseManager()
        MainPage(self.db_manager, master)
        #DevPage(master)


root = tk.Tk()
myapp = App(root)
root.geometry("1000x400")
root.mainloop()