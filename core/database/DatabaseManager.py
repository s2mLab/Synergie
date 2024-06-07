import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import numpy as np

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
        cred = credentials.Certificate('s2m-skating-firebase-adminsdk-3ofmb-8552d58146.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://s2m-skating-default-rtdb.firebaseio.com/'
        }
        )

        self.ref = db.reference('/')

    def save_skater_data(self, data : SkaterData) -> int:
        if self.ref.child("Skater").get() is None:
            newKey = self.ref.child("Skater").push().key
            self.ref.child("Skater").update({newKey:
                {"skater_id" : 1,
                "skater_name" : data.skater_name}
            })
        else:
            newId = self.ref.child("Skater").order_by_key().get().popitem()[1].get("skater_id")+1
            newKey = self.ref.child("Skater").push().key
            self.ref.child("Skater").update({newKey : 
                {"skater_id" : newId,
                "skater_name" : data.skater_name}
            }) 
        new_id = self.ref.child("Skater").order_by_key().get().popitem()[1].get("skater_id")
        return new_id
    
    def save_training_data(self, data : TrainingData) -> int:
        if self.ref.child("Training").get() is None:
            newKey = self.ref.child("Training").push().key
            self.ref.child("Training").update({newKey :
                {"training_id" : 1,
                "skater_id" : data.skater_id,
                "training_date" : data.training_date.isoformat(sep=' ', timespec='minutes')}
            })
        else:
            newId = self.ref.child("Training").order_by_key().get().popitem()[1].get("training_id")+1
            newKey = self.ref.child("Training").push().key
            self.ref.child("Training").update({newKey :
                {"training_id" : newId,
                "skater_id" : data.skater_id,
                "training_date" : data.training_date.isoformat(sep=' ', timespec='minutes')}
            }) 
        new_id = self.ref.child("Training").order_by_key().get().popitem()[1].get("training_id")
        return new_id
    
    def save_jump_data(self, data : JumpData) -> int:
        if self.ref.child("Jump").get() is None:
            newKey = self.ref.child("Jump").push().key
            self.ref.child("Jump").update({newKey :
                {"jump_id" : 1,
                "training_id" : data.training_id,
                "jump_type" : data.jump_type,
                "jump_rotations" : data.jump_rotations,
                "jump_success" : data.jump_success,
                "jump_time" : data.jump_time}
            })
        else:
            newId = self.ref.child("Jump").order_by_key().get().popitem()[1].get("jump_id")+1
            newKey = self.ref.child("Jump").push().key
            self.ref.child("Jump").update({newKey :
                {"jump_id" : newId,
                "training_id" : data.training_id,
                "jump_type" : data.jump_type,
                "jump_rotations" : data.jump_rotations,
                "jump_success" : data.jump_success,
                "jump_time" : data.jump_time}
            }) 
        new_id = self.ref.child("Jump").order_by_key().get().popitem()[1].get("jump_id")
        return new_id

    def load_skater_data(self, skater_id : int) -> list[TrainingData]:
        data_trainings = []
        for val in self.ref.child("Training").order_by_key().get().values():
            if val["skater_id"] == skater_id:
                data_trainings.append(TrainingData(int(val["training_id"]), int(val["skater_id"]), datetime.strptime(val["training_date"], '%Y-%m-%d %H:%M')))
        data_trainings = np.array(data_trainings)
        return data_trainings

    def load_training_data(self, training_id : int) -> list[JumpData]:
        data_jumps = []
        for val in self.ref.child("Jump").order_by_key().get().values():
            if val["training_id"] == training_id:
                data_jumps.append(JumpData(int(val["jump_id"]), int(val["training_id"]), int(val["jump_type"]), float(val["jump_rotations"]), bool(val["jump_success"]), int(val["jump_time"])))
        data_jumps = np.array(data_jumps)
        return data_jumps
    
    def get_skater_from_training(self, training_id : int) -> int:
        name = []
        for val in self.ref.child("Training").order_by_key().get().values():
            if val["training_id"] == training_id:
                name.append(val)
        return int(name[0]["skater_id"])

    def get_skater_name_from_id(self, skater_id : int) -> str:
        name = []
        for val in self.ref.child("Skater").order_by_key().get().values():
            if val["skater_id"] == skater_id:
                name.append(val)
        return name[0]["skater_name"]
    
    def get_all_skaters(self) -> list[SkaterData]:
        data_skaters = []
        for val in self.ref.child("Skater").order_by_key().get().values():
            data_skaters.append(SkaterData(int(val["skater_id"]), val["skater_name"]))
        return data_skaters
    
    def delete_skater_data(self, skater_id : int) -> None:
        deleted_key = 0
        for key, val in self.ref.child("Skater").order_by_key().get().items():
            if int(val["skater_id"]) == int(skater_id):
                deleted_key = key
        self.ref.child(f"Skater/{deleted_key}").delete()