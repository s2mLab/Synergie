import tkinter as tk

from core.database.DatabaseManager import DatabaseManager, SkaterData

class ManagementPage:
    def __init__(self, db_manager : DatabaseManager) -> None:
        self.db_manager = db_manager
        self.frame = tk.Frame()
        self.management_input()

    def create_page(self, main):
        self.main = main
        self.create_table()
        self.frame.grid()

    def management_input(self):
        tk.Label(self.frame, text="Enter a name").grid(row=0,column=0)
        self.entryadd = tk.Entry(self.frame)
        self.contentsadd = tk.StringVar()
        self.entryadd["textvariable"] = self.contentsadd
        self.entryadd.grid(row=1,column=0)
        tk.Button(self.frame, text="Add a new skater", command = self.add_windows).grid(row=2,column=0)

        tk.Label(self.frame, text="Enter a number").grid(row=4,column=0)
        self.entrydelete = tk.Entry(self.frame)
        self.contentsdelete = tk.StringVar()
        self.entrydelete["textvariable"] = self.contentsdelete
        self.entrydelete.grid(row=5,column=0)
        tk.Button(self.frame, text="Delete a skater", command = self.delete_windows).grid(row=6,column=0)

        tk.Button(self.frame, text='Go to Main Page',
                  command=self.return_main_page).grid(row=10, column=10, sticky="se")

    def return_main_page(self) -> None:
        self.frame.grid_forget()
        self.main.grid()

    def add_windows(self):
        self.open_confirm_window("You really want to add a new skater ?", self.add_skater)
    
    def delete_windows(self):
        self.open_confirm_window("You really want to delete a skater ?", self.delete_skater)

    def add_skater(self):
        skater_name = self.contentsadd.get()
        self.db_manager.save_skater_data(SkaterData(0, skater_name))
        self.reload_page()
        self.confirm_window.destroy()

    def delete_skater(self):
        skater_id = self.contentsdelete.get()
        self.db_manager.delete_skater_data(skater_id)
        self.reload_page()
        self.confirm_window.destroy()

    def create_table(self):
        data_skaters = self.db_manager.get_all_skaters()
        for i,skater in enumerate(data_skaters):
            entry = tk.Entry(self.frame)
            entry.grid(row=i,column=1)
            entry.insert(0,skater.skater_id)
            entry = tk.Entry(self.frame)
            entry.grid(row=i,column=2)
            entry.insert(0,skater.skater_name)

    def reload_page(self):
        self.frame.destroy()
        self.frame = tk.Frame()
        self.management_input()
        self.create_table()
        self.frame.grid()

    def open_confirm_window(self, message : str, action):
        self.confirm_window = tk.Toplevel()
        frame = tk.Frame(self.confirm_window, height=100, width=200)
        tk.Label(frame, text=message).grid(row=0,column=0,columnspan=2)
        tk.Button(frame, text="Yes", command=action).grid(row=1,column=0)
        tk.Button(frame, text="No", command=self.cancel_action).grid(row=1,column=1)
        frame.grid()

    def cancel_action(self):
        self.confirm_window.destroy()