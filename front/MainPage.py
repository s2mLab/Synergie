import threading
from tkinter.font import BOLD, Font
from typing import List
import ttkbootstrap as ttkb

from core.utils.DotDevice import DotDevice
from core.database.DatabaseManager import DatabaseManager
from core.utils.DotManager import DotManager
from front.DotPage import DotPage

from front.ExtractingPage import ExtractingPage

class MainPage:
    def __init__(self, dotsConnected : List[DotDevice], dot_manager : DotManager, db_manager : DatabaseManager, root :ttkb.Window = None) -> None:
        self.root = root
        self.dotsConnected = dotsConnected
        self.dot_manager = dot_manager
        self.db_manager = db_manager
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame = ttkb.Frame(root)
        self.frame.grid_rowconfigure(0,weight=1,pad=50)
        self.frame.grid_rowconfigure(1,weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        buttonStyle = ttkb.Style()
        buttonStyle.configure('home.TButton', font=Font(self.frame, size=20, weight=BOLD))
        labelFont = Font(self.root, size=15, weight=BOLD)
        self.waitingFrame = ttkb.Frame(self.frame)
        waitingLabel= ttkb.Label(self.waitingFrame, text="Waiting for connection", font=labelFont)
        waitingLabel.grid(row=0,column=0,pady=50)
        waitingProgress = ttkb.Progressbar(self.waitingFrame, mode='indeterminate', length=200)
        waitingProgress.grid(row=1,column=0)
        waitingProgress.start(10)
        self.waitingFrame.grid(row=0,column=0)
        self.frame.grid(sticky="nswe")
    
    def make_dot_page(self):
        self.waitingFrame.destroy()
        self.dotPage = DotPage(self.frame, self.dotsConnected)
        self.dotPage.grid(row=0,column=0,sticky="nswe")
        self.make_export_button()
        self.frame.update()
        self.run_periodic_background_func()
    
    def make_export_button(self):
        self.estimatedTime = self.dot_manager.getExportEstimatedTime()
        self.exportFrame = ttkb.Frame(self.frame)
        ttkb.Button(self.exportFrame, text=f'Export data from all sensors, estimated time : {round(self.estimatedTime,0)} min', style="home.TButton", command=self.export_all_dots).grid(row=0, column=0)
        self.saveFile = ttkb.Checkbutton(self.exportFrame, text="Save extra data (for research)")
        self.saveFile.state(['!alternate'])
        self.saveFile.grid(row=1,column=0)
        self.exportFrame.grid(row=1,column=0)

    def export_all_dots(self):
        for device in self.dotsConnected:
            if (not device.isRecording) and device.isPlugged and device.recordingCount > 0:
                extractEvent = threading.Event()
                threading.Thread(target=device.exportData, args=([self.saveFile, extractEvent]),daemon=True).start()
                ExtractingPage(device.deviceTagName, self.estimatedTime, extractEvent)

    def run_periodic_background_func(self):
        self.dotPage.updatePage()
        self.root.after(1000,self.run_periodic_background_func)