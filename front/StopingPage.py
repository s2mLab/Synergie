import threading
import time
from PIL import Image, ImageTk
from tkinter.font import BOLD, Font
import ttkbootstrap as ttkb

from core.database.DatabaseManager import DatabaseManager
from core.utils.DotDevice import DotDevice

class StopingPage:
    def __init__(self, device : DotDevice, db_manager : DatabaseManager) -> None:
        self.device = device
        self.db_manager = db_manager
        self.deviceTag = self.device.deviceTagName
        self.window = ttkb.Toplevel(title="Confirmation", size=(1000,400), topmost=True)
        self.window.place_window_center()
        ico = Image.open('img/Logo_s2mJUMP_RGB.png')
        photo = ImageTk.PhotoImage(ico)
        self.window.wm_iconphoto(False, photo)
        self.window.grid_rowconfigure(0, weight = 1)
        self.window.grid_columnconfigure(0, weight = 1)
        self.frame = ttkb.Frame(self.window)
        self.frame.grid_rowconfigure(0, weight = 0)
        self.frame.grid_rowconfigure(1, weight = 1)
        self.frame.grid_rowconfigure(2, weight = 1)
        self.frame.grid_columnconfigure(0, weight = 1)
        label = ttkb.Label(self.frame, text=f"Stoping a training on sensor {self.deviceTag}", font=Font(self.window, size=20, weight=BOLD))
        label.grid(row=0,column=0,pady=20)
        buttonStyle = ttkb.Style()
        buttonStyle.configure('my.TButton', font=Font(self.frame, size=12, weight=BOLD))
        ttkb.Button(self.frame, text="Stop", style="my.TButton", command=self.stopRecord).grid(row=1,column=0,sticky="nsew",pady=20)
        self.estimatedTime = self.device.getExportEstimatedTime()
        ttkb.Button(self.frame, text=f"Stop and extract data \n Estimated time : {round(self.estimatedTime,0)} min", style="my.TButton", command=self.stopRecordAndExtract).grid(row=2,column=0,sticky="nsew")
        self.saveFile = ttkb.Checkbutton(self.frame, text="Save extra data (for research)")
        self.saveFile.state(['!alternate'])
        self.saveFile.grid(row=3,column=0,sticky="nsew")
        self.frame.grid(sticky ="nswe")
        self.window.grid()

    def stopRecord(self):
        recordStopped = self.device.stopRecord()
        self.frame.destroy()
        self.frame = ttkb.Frame(self.window)
        if recordStopped :
            message = f"Record stopped on sensor {self.deviceTag}"
        else : 
            message = "Error during process, cannot stop the recording"
        label = ttkb.Label(self.frame, text=message, font=Font(self.window, size=20, weight=BOLD))
        label.grid()
        self.frame.grid()
        self.window.update()
        time.sleep(1)
        self.window.destroy()
    
    def stopRecordAndExtract(self):
        recordStopped = self.device.stopRecord()
        if recordStopped:
            self.device.currentImage = self.device.imageInactive
        saveFile = self.saveFile.instate(["selected"])
        self.frame.destroy()
        self.frame = ttkb.Frame(self.window)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        if recordStopped :
            message = f"Record stopped on sensor {self.deviceTag}"
        else : 
            message = "Error during process, cannot stop the recording"
        self.text = ttkb.StringVar(self.frame, value = message)
        self.label = ttkb.Label(self.frame, textvariable=self.text, font=Font(self.window, size=20, weight=BOLD))
        self.label.grid(row=0,column=0, pady=50)
        self.frame.grid()
        self.window.update()
        time.sleep(1)
        self.text.set(f"Extracting data from sensor {self.deviceTag} \nDo not disconnect this sensor")
        self.label.update()
        self.max_val = 60*self.estimatedTime
        self.progressExtract = ttkb.Progressbar(self.frame, value=0, maximum=self.max_val, style='success.Striped.Horizontal.TProgressbar', mode="determinate")
        self.progressExtract.start(1000)
        self.progressExtract.grid(row=1, column=0, sticky="we")
        self.frame.grid()
        self.window.update()
        self.extractEvent = threading.Event()
        self.checkFinish()
        if recordStopped :
            threading.Thread(target=self.device.exportData, args=([saveFile, self.extractEvent]),daemon=True).start()
        else:
            self.extractEvent.set()

    def checkFinish(self):
        try:
            self.checkProgressBar()
        except:
            pass
        self.window.update()
        if self.extractEvent.is_set():
            self.text.set("Extraction finish")
            self.label.update()
            time.sleep(1)
            self.window.destroy()
        self.window.after(1000, self.checkFinish)
    
    def checkProgressBar(self):
        if self.progressExtract["value"] >= self.max_val-1: 
            self.progressExtract.stop()
            self.progressExtract["value"] = self.max_val