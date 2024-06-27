from queue import Queue
import tkinter as tk
import numpy as np

from core.database.DatabaseManager import DatabaseManager
from front.DotPage import DotPage
from front.management.ManagementPage import ManagementPage
from front.visualization.SkaterPage import SkaterPage

class RecordPage:
    def __init__(self, db_manager : DatabaseManager, infoqueue: Queue) -> None:
        self.db_manager = db_manager
        self.infoqueue = infoqueue
        self.confirm_window = tk.Toplevel()
        self.frame = tk.Frame(self.confirm_window, height=100, width=200)
        
    def sendSkaterName(self, entry) -> str:
        self.infoqueue.put(entry.get())
        self.confirm_window.destroy()
    
    def createPage(self) -> None:
        tk.Label(self.frame, text='Enter a skater name').grid(row=0, column=0)
        entryvar = tk.StringVar()
        entry = tk.Entry(self.frame, textvariable=entryvar)
        entry.grid(row=1,column=0)
        tk.Button(self.frame, text="Start Record", command=lambda : self.sendSkaterName(entry)).grid(row=2,column=0)
        self.frame.grid()