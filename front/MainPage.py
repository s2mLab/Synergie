import tkinter as tk
import numpy as np

from core.database.DatabaseManager import DatabaseManager
from front.management.ManagementPage import ManagementPage
from front.visualization.SkaterPage import SkaterPage

class MainPage:
    def __init__(self, db_manager : DatabaseManager, root=None) -> None:
        self.db_manager = db_manager
        self.root = root
        self.frame = tk.Frame(self.root)
        self.frame.grid()
        tk.Label(self.frame, text='Main page').grid(row=0, column=1)
        tk.Button(self.frame, text='Go to Skater Page',
                  command=self.make_management_page).grid(row=1, column=0)
        tk.Button(self.frame, text='Go to Stats Page',
                  command=self.make_visualize_page).grid(row=1, column=2)

    def create_page(self) -> None:
        self.frame.grid()

    def make_visualize_page(self) -> None:
        self.frame.grid_forget()
        SkaterPage(self.db_manager).create_page(self.frame)
    
    def make_management_page(self) -> None:
        self.frame.grid_forget()
        ManagementPage(self.db_manager).create_page(self.frame)