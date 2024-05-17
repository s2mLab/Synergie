import tkinter as tk
from tkinter import ttk

from dateutil.relativedelta import relativedelta
from datetime import datetime

from core.database.DatabaseManager import JumpData, TrainingData


class TimelineSkater(tk.Frame):
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
        header_text = kwargs.pop("header", "Skater")
        trainings : list[TrainingData]= kwargs.pop("trainings", [])
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
        years_showed = []
        months_showed = []
        for i,training in enumerate(trainings):
            year = training.training_date.year
            month = training.training_date.strftime("%b")
            if not (year in years_showed and month in months_showed):
                month_label = tk.Label(
                    self.inner_frame, text= f"{month} {year}", background=bg, anchor="w"
                )
                month_label.grid(row=0, column=i, sticky="ew")
            years_showed.append(year)
            months_showed.append(month)
            day = training.training_date.day
            if day == 1:
                day = f"{day}st"
            elif day == 2:
                day = f"{day}nd"
            elif day == 3:
                day = f"{day}rd"
            else:
                day = f"{day}th"
            hour = training.training_date.hour
            minute = training.training_date.minute
            label = tk.Label(self.inner_frame, text=f"{day} {hour}:{minute}", anchor="w", background=bg)
            button = tk.Label(
                self.inner_frame,
                text="    ",
                width=6,
                bd=0,
                relief="flat",
                bg="grey",
            )
            label.grid(row=1, column=i, padx=2, sticky="ew")
            button.grid(row=2, column=i, padx=2, sticky="ew")
            button.bind(
                "<1>",
                lambda event, training=training: self._callback(event, training.training_id),
            )

            self.buttons[i] = button

        self.canvas.bind("<Configure>", self._resize)

    def _callback(self, event, training_id):
        if self.command:
            self.command(training_id = training_id)

    def _resize(self, event):
        self.canvas.configure(height=self.inner_frame.winfo_height())
        bbox = self.canvas.bbox("all")
        self.canvas.configure(scrollregion=bbox)