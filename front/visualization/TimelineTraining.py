import tkinter as tk
from tkinter import ttk

from dateutil.relativedelta import relativedelta
from datetime import datetime

from core.database.DatabaseManager import JumpData


class TimelineTraining(tk.Frame):
    """
    Timeline widget

    options:
      command     command to be called when user clicks on a month
      header_text text for the header. Defaults to "Date"
      start_date  datetime representing the start of the timeline
      end_date    datetime representing the end of the timeline
      kwargs      additional arguments passed to the superclass
                  (useful for setting colors, borderwidth)

    subcommands;
      highlight   takes one or more arguments that are a tuple of
                  (month,year). kwargs can be bg to set the background,
                  and fg to set the foreground
    """

    def __init__(self, parent, **kwargs):
        header_text = kwargs.pop("header", "Training")
        jumps : list[JumpData]= kwargs.pop("jumps", [])
        self.command = kwargs.pop("command", None)

        super().__init__(parent, **kwargs)

        bg = self.cget("background")
        self.header = tk.Label(self, text=header_text, background=bg, anchor="w")
        self.sep = ttk.Separator(self, orient="horizontal")
        self.canvas = tk.Canvas(self, background=bg)
        self.scrollbar = tk.Scrollbar(
            self, orient="horizontal", command=self.canvas.xview
        )
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.header.pack(side="top", fill="x")
        self.sep.pack(side="top", fill="x")
        self.canvas.pack(side="top", fill="x")
        self.scrollbar.pack(side="top", fill="x")

        self.inner_frame = tk.Frame(self.canvas, background=bg)
        self.canvas.create_window(0, 0, anchor="nw", window=self.inner_frame)

        self.buttons = {}
        for i,jump in enumerate(jumps):
            index = f"{jump.jump_time//60}:{jump.jump_time%60}"
            label = tk.Label(self.inner_frame, text=index, anchor="w", background=bg)
            if jump.jump_success:
                back = "green"
            else:
                back = "red"
            button = tk.Label(
                self.inner_frame,
                text="    ",
                width=6,
                bd=0,
                relief="flat",
                bg=back,
            )
            label.grid(row=1, column=i, padx=2, sticky="ew")
            button.grid(row=2, column=i, padx=2, sticky="ew")
            button.bind(
                "<1>",
                lambda event, jump=jump: self._callback(event, jump.jump_type, jump.jump_rotations, jump.jump_success),
            )

            self.buttons[i] = button

        self.canvas.bind("<Configure>", self._resize)

    def _callback(self, event, type, rotations, success):
        if self.command:
            self.command(type = type, rotations = rotations, success = success)

    def _resize(self, event):
        self.canvas.configure(height=self.inner_frame.winfo_height())
        bbox = self.canvas.bbox("all")
        self.canvas.configure(scrollregion=bbox)
