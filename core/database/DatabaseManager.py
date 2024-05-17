import numpy as np
from cs50 import SQL

from dataclasses import dataclass
from datetime import datetime

@dataclass
class JumpData:
    jump_id : int
    training_id : int
    jump_type : int
    jump_rotations : float
    jump_success : bool
    jump_time : int

@dataclass
class TrainingData:
    training_id : int
    skater_id : int
    training_date : datetime

@dataclass
class SkaterData:
    skater_id : int
    skater_name : str

class DatabaseManager:
    def __init__(self):
        self.db = SQL("sqlite:///database/database.db")
    
    def save_skater_data(self, data : SkaterData) -> int:
        new_id = self.db.execute("INSERT INTO skater (skater_name) VALUES (?)", data.skater_name)
        return new_id
    
    def save_training_data(self, data : TrainingData) -> int:
        new_id = self.db.execute("INSERT INTO training (skater_id, training_date) VALUES (?,?)", data.skater_id, data.training_date)
        return new_id
    
    def save_jump_data(self, data : JumpData) -> int:
        new_id = self.db.execute("INSERT INTO jump (training_id, jump_type, jump_rotations, jump_success, jump_time) VALUES (?,?,?,?,?)", data.training_id, data.jump_type, data.jump_rotations, data.jump_success, data.jump_time)
        return new_id

    def load_skater_data(self, skater_id : int) -> list[TrainingData]:
        data_trainings = self.db.execute("SELECT training_id, skater_id, training_date FROM training WHERE skater_id == ? ORDER BY training_date", skater_id)
        if len(data_trainings)>0:
            data_trainings = np.vectorize(lambda x : TrainingData(int(x["training_id"]), int(x["skater_id"]), datetime.strptime(x["training_date"], '%Y-%m-%d %H:%M:%S')))(data_trainings)
        return data_trainings

    def load_training_data(self, training_id : int) -> list[JumpData]:
        data_jumps= self.db.execute("SELECT jump_id, training_id, jump_type, jump_rotations, jump_success, jump_time FROM jump WHERE training_id == ? ORDER BY jump_time", training_id)
        if len(data_jumps)>0:
            data_jumps = np.vectorize(lambda x : JumpData(int(x["jump_id"]), int(x["training_id"]), int(x["jump_type"]), float(x["jump_rotations"]), bool(x["jump_success"]), int(x["jump_time"])))(data_jumps)
        return data_jumps
    
    def get_skater_from_training(self, training_id : int) -> int:
        name = self.db.execute("SELECT skater_id FROM skater NATURAL JOIN training WHERE training_id == ?", training_id)
        return int(name[0]["skater_id"])

    def get_skater_name_from_id(self, skater_id : int) -> str:
        name = self.db.execute("SELECT skater_name FROM skater WHERE skater_id == ?", skater_id)
        return name[0]["skater_name"]
    
    def get_all_skaters(self) -> list[SkaterData]:
        data_skaters = self.db.execute("SELECT skater_id, skater_name FROM skater ")
        if len(data_skaters)>0:
            data_skaters = np.vectorize(lambda x : SkaterData(int(x["skater_id"]), x["skater_name"]))(data_skaters)
        return data_skaters
    
    def delete_skater_data(self, skater_id : int) -> None:
        self.db.execute("DELETE FROM skater WHERE skater_id == ?", skater_id)
        