import time
from PIL import Image, ImageTk
import ttkbootstrap as ttkb
from tkinter import messagebox
import threading

from front.ConnectionPage import ConnectionPage
from core.data_treatment.data_generation.exporter import export
from core.database.DatabaseManager import *
from core.utils.DotManager import DotManager
from front.StartingPage import StartingPage
from front.StopingPage import StopingPage
from front.MainPage import MainPage

class App:

    def __init__(self, root : ttkb.Window):
        self.db_manager = DatabaseManager()
        self.dot_manager = DotManager(self.db_manager)
        self.root = root

        self.connectionPage = ConnectionPage(self.root, self.db_manager)
        self.checkConnection()

    def checkConnection(self):
        if self.connectionPage.userConnected != "":
            self.userConnected = self.connectionPage.userConnected
            self.connectionPage.frame.destroy()
            self.root.update()
            self.launchMainPage()
        else:
            self.root.after(100, self.checkConnection)

    def launchMainPage(self):
        self.mainPage = MainPage([], self.dot_manager, self.db_manager, self.root)
        self.initialEvent = threading.Event()
        threading.Thread(target=self.initialize, args=([self.initialEvent]), daemon=True).start()
        self.checkInit()
    
    def checkInit(self):
        if self.initialEvent.is_set():
            self.mainPage.dotsConnected = self.dot_manager.getDevices()
            self.mainPage.make_dot_page()
            self.initialEvent.clear()
        else:
            self.root.after(100, self.checkInit)

    def initialize(self, initialEvent : threading.Event):
        (check, unconnectedDevice) = self.dot_manager.firstConnection()
        while not check:
            deviceMessage = f"{unconnectedDevice[0]}"
            for deviceTag in unconnectedDevice[1:]:
                deviceMessage = deviceMessage + " ," + deviceTag 
            messagebox.askretrycancel("Connexion", f"Veuillez reconnecter les capteurs {deviceMessage}")
            (check, unconnectedDevice) = self.dot_manager.firstConnection()

        initialEvent.set()

        usb_detection_thread = threading.Thread(target=self.checkUsbDots, args=([self.startStopping, self.startStarting]))
        usb_detection_thread.daemon = True
        usb_detection_thread.start()

    def checkUsbDots(self, callbackStop, callbackStart):
        while True:
            checkUsb = self.dot_manager.checkDevices()
            lastConnected = checkUsb[0]
            lastDisconnected = checkUsb[1]
            if lastConnected:
                print("Connexion")
                for device in lastConnected:
                    if device.isRecording or device.recordingCount > 0 :
                        callbackStop(device)
            if lastDisconnected:
                print("Deconnexion")
                for device in lastDisconnected:
                    if not device.isRecording:
                        callbackStart(device)
            time.sleep(0.2)

    def startStopping(self, device):
        StopingPage(device, self.db_manager)
    
    def startStarting(self, device):
        StartingPage(device, self.db_manager, self.userConnected)

root = ttkb.Window(title="Synergie", themename="minty")
myapp = App(root)
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.geometry("%dx%d" % (width, height))
try :
    ico = Image.open(f'{sys._MEIPASS}/img/Logo_s2mJUMP_RGB.png')
except:
    ico = Image.open(f'img/Logo_s2mJUMP_RGB.png')
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)
root.mainloop()
