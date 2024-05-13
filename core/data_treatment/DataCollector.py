import os

import pandas as pd
import numpy as np

import constants
from datetime import datetime
from core.database.DatabaseManager import *


def save_training_session(path, db_manager : DatabaseManager):

        unique_training_dict = {}
        
        df = pd.read_csv(path)
        for x in np.unique(df["skater_name"].to_numpy()):
            training_data = TrainingData(0, int(x), datetime.now())
            new_id = db_manager.save_training_data(training_data)
            unique_training_dict[x] = new_id

        for iter,row in df.iterrows():
            jump_time_min, jump_time_sec = row["videoTimeStamp"].split(":")
            jump_time = int(jump_time_min)*60 + int(jump_time_sec)
            jump_data = JumpData(0, int(unique_training_dict[row["skater_name"]]), int(row["type"]), float(row["rotations"]), bool(row["success"]), jump_time)
            db_manager.save_jump_data(jump_data)

def get_all_skater_training(skater_id : int, db_manager : DatabaseManager):
    data = db_manager.load_skater_data(skater_id)
    print(data)

def get_training_session_data(training_id : int, db_manager : DatabaseManager):
    data = db_manager.load_training_data(training_id)
    skater_name = db_manager.get_skater_from_training(training_id)
    jump_types = np.zeros((6,2))
    for jump in data:
         jump_types[jump.jump_type,jump.jump_success] += 1
    dict_jump = {}
    for i in constants.jumpType:
         if i.value <6:
            dict_jump[i.name] = jump_types[i.value].tolist()
    return dict_jump

