from math import ceil
import ttkbootstrap as ttkb
from typing import List

from core.utils.DotDevice import DotDevice
from front.DotFrame import DotFrame

class DotPage(ttkb.Frame):
    def __init__(self, parent, dotsconnected : List[DotDevice], **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.dotsFrames : List[DotFrame] = []
        self.frame = ttkb.Frame(self.parent)
        for i in range(ceil(len(dotsconnected)/5)):
            self.frame.grid_rowconfigure(i, weight=1, pad=50)
        for i in range(5):
            self.frame.grid_columnconfigure(i, weight=1, pad=50)
        for i,device in enumerate(dotsconnected):
            newdot = DotFrame(self.frame, device)
            self.dotsFrames.append(newdot)
            newdot.grid(row=i//5, column=i%5)
        self.frame.grid(row=0, column=0, sticky="nswe")
    
    def updatePage(self):
        for dotFrame in self.dotsFrames:
            dotFrame.updateDot()
