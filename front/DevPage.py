import tkinter as tk
import os

import constants
from core.data_treatment.data_generation.exporter import export
from core.model import model
from core.data_treatment.data_generation.modelPredictor import ModelPredictor
from core.database.DatabaseManager import *
from core.data_treatment import DataCollector

class DevPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        # Create the application variable.
        self.contents = tk.StringVar()
        # Set it to some value.
        self.contents.set("1331")
        self.options = ["1404","1304","1331","1414","1128"]

        self.entrythingy = tk.OptionMenu(master, self.contents, *self.options)
        self.entrythingy.pack()
        # Tell the entry widget to watch this variable.
        self.entrythingy["textvariable"] = self.contents

        self.exportButton = tk.Button(text="Export")
        self.exportButton.pack()
        self.testButton = tk.Button(text="Test")
        self.testButton.pack()
        self.save_button = tk.Button(text="Save")
        self.save_button.pack()

        # Define a callback for when the user hits return.
        # It prints the current value of the variable.
        self.entrythingy.bind('<Key-Return>',
                             self.print_contents)
        self.exportButton.bind('<Button>',self.export_contents)
        self.testButton.bind('<Button>',self.test_contents)
        self.save_button.bind('<Button>',self.save_data)

        self.resultType = tk.Entry()
        self.resultType.pack()
        self.resultSuccess = tk.Entry()
        self.resultSuccess.pack()

        self.db_manager = DatabaseManager()

        self.skater_button = tk.Button(text="Skater")
        self.skater_button.pack()

        self.training_button = tk.Button(text="Training")
        self.training_button.pack()

        self.skater_button.bind('<Button>', self.skater_data)
        self.training_button.bind('<Button>', self.training_data)

        self.dbcontents = tk.StringVar()
        self.dbentry = tk.Entry()
        self.dbentry.pack()
        self.dbentry["textvariable"] = self.dbcontents

    def print_contents(self, event):
        print("Hi. The current entry content is:",
              self.contents.get())
        
    def export_contents(self, event):
        session_name = self.contents.get()
        session = constants.sessions[session_name]
        if session is None:
            raise Exception("session not found")
        export(session["path"], session["sample_time_fine_synchro"])

    def test_contents(self, event):
        session_name = self.contents.get()
        session = constants.sessions[session_name]
        path_anno = os.path.join("data/annotated/",session["path"])
        path_pend = os.path.join("data/pending/",session["path"])
        model_test_type = model.load_model(constants.modeltype_filepath)
        model_test_success = model.load_model(constants.modelsuccess_filepath)
        error_type = ModelPredictor(path_pend,model_test_type, model_test_success).checktype(path_anno)
        error_success = ModelPredictor(path_pend,model_test_type, model_test_success).checksuccess(path_anno)
        self.resultType.insert(0, error_type)
        self.resultSuccess.insert(0, error_success)

    def save_data(self, event):
        session_name = self.contents.get()
        session = constants.sessions[session_name]
        path_data = os.path.join("data/pending/",session["path"],"jumplist.csv")
        DataCollector.save_training_session(path_data, self.db_manager)
        print("OK")

    def skater_data(self, event):
        skater_id = int(self.dbcontents.get())
        DataCollector.get_all_skater_training(skater_id, self.db_manager)

    def training_data(self, event):
        training_id = int(self.dbcontents.get())
        DataCollector.get_training_session_data(training_id, self.db_manager)