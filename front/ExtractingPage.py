import threading
import time
from tkinter.font import BOLD, Font
import ttkbootstrap as ttkb

class ExtractingPage:
    def __init__(self, deviceTag : str, estimatedTime, event : threading.Event) -> None:
        self.deviceTag = deviceTag
        self.event = event
        self.window = ttkb.Toplevel(title="Confirmation", size=(1000,400), topmost=True)
        self.window.place_window_center()
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        self.text = ttkb.StringVar(self.window, value = f"Extracting data from sensor {self.deviceTag} \nDo not disconnect this sensor")
        self.label = ttkb.Label(self.window, textvariable=self.text, font=Font(self.window, size=20, weight=BOLD))
        self.label.grid(row=0,column=0)
        self.max_val = 60*estimatedTime
        self.progressExtract = ttkb.Progressbar(self.window, value=0, maximum=self.max_val, length=self.label.winfo_reqwidth(), style='success.Striped.Horizontal.TProgressbar', mode="determinate")
        self.progressExtract.start(1000)
        self.progressExtract.grid(row=1, column=0)
        self.checkFinish()

    def checkFinish(self):
        try:
            self.checkProgressBar()
        except:
            pass
        if self.event.is_set():
            self.text.set("Extraction finish")
            self.label.update()
            time.sleep(1)
            self.window.destroy()
        self.window.after(1000, self.checkFinish)
    
    def checkProgressBar(self):
        if self.progressExtract["value"] >= self.max_val-1: 
            self.progressExtract.stop()
            self.progressExtract["value"] = self.max_val