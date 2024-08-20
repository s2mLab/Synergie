import time
from tkinter import VERTICAL
from PIL import Image, ImageTk
from tkinter.font import BOLD, Font
from math import ceil
import ttkbootstrap as ttkb

from core.utils.DotDevice import DotDevice
from core.database.DatabaseManager import DatabaseManager, TrainingData

class StartingPage:
    def __init__(self, device : DotDevice, db_manager : DatabaseManager, userConnected : str) -> None:
        self.device = device
        self.db_manager = db_manager
        self.deviceTag = self.device.deviceTagName
        self.skaters = self.db_manager.getAllSkaterFromCoach(userConnected)

        self.window = ttkb.Toplevel(title="Confirmation", size=(1400,400), topmost=True)
        self.window.place_window_center()
        ico = Image.open('img/Logo_s2mJUMP_RGB.png')
        photo = ImageTk.PhotoImage(ico)
        self.window.wm_iconphoto(False, photo)
        self.window.grid_rowconfigure(0, weight=0)
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1, pad=20)
        self.window.grid_columnconfigure(1, weight=0)

        self.label = ttkb.Label(self.window, text=f"Starting a training on sensor {self.deviceTag}", font=Font(self.window, size=20, weight=BOLD))
        self.label.grid(row=0,column=0,columnspan=2, pady=20)

        self.canvas = ttkb.Canvas(self.window)
        self.canvas.grid_rowconfigure(0, weight = 1)
        self.canvas.grid_columnconfigure(0, weight = 1)

        self.frame = ttkb.Frame(self.canvas)
        self.frame.grid_rowconfigure(0, weight = 1)
        self.frame.grid_rowconfigure(1, weight = 1)
        self.frame.grid_columnconfigure(0, weight = 1)
        self.frame.grid_columnconfigure(1, weight = 1)
        self.frame.grid_columnconfigure(2, weight = 1)
        self.frame.grid_columnconfigure(3, weight = 1)
        self.frame.grid_columnconfigure(4, weight = 1)

        buttonStyle = ttkb.Style()
        buttonStyle.configure('my.TButton', font=Font(self.frame, size=12, weight=BOLD))
        for i,skater in enumerate(self.skaters):
            button = ttkb.Button(self.frame, text=f"\n{skater.skater_name}\n", style="my.TButton", width=ceil((250-24)/11), command=(lambda x=skater.skater_id,y=skater.skater_name: self.startRecord(x,y)))
            button.grid(row=i//5+1,column=i%5,padx=10,pady=10)
        
        self.frame.bind('<Enter>', self._bound_to_mousewheel)
        self.frame.bind('<Leave>', self._unbound_to_mousewheel)

        self.frame.grid(row=0, column=0, sticky="nswe")
        
        scroll = ttkb.Scrollbar(self.window, orient=VERTICAL, command=self.canvas.yview)
        scroll.grid(row=1,column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.bind(
            '<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.frame, anchor="center")

        self.canvas.grid(row=1,column=0, sticky="nswe", padx=10)

        self.window.grid()

    def startRecord(self ,skaterId: str, skaterName: str):
        deviceId = self.device.deviceId
        new_training = TrainingData(0, skaterId, 0, deviceId, [])
        self.db_manager.set_current_record(deviceId, self.db_manager.save_training_data(new_training))
        recordStarted = self.device.startRecord()
        self.canvas.destroy()
        self.label.destroy()
        self.frame = ttkb.Frame(self.window)
        if recordStarted :
            message = f"Record started on sensor {self.deviceTag} for {skaterName}"
        else : 
            message = "Error during process, cannot start the recording"
        label = ttkb.Label(self.frame, text=message, font=Font(self.window, size=20, weight=BOLD))
        label.grid()
        self.frame.grid(row=1,column=0)
        self.window.update()
        time.sleep(1)
        self.canvas.destroy()
        self.window.destroy()
    
    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")