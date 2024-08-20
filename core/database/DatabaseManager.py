from typing import List
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin.firestore

from dataclasses import dataclass
from datetime import datetime

@dataclass
class JumpData:
    jump_id : int
    training_id : int
    jump_type : str
    jump_rotations : float
    jump_success : bool
    jump_time : int
    jump_max_speed : float
    jump_length : float

    def to_dict(self):
        return {"training_id" : self.training_id,
         "jump_type" : self.jump_type,
         "jump_rotations" : self.jump_rotations,
         "jump_success" : self.jump_success,
         "jump_time" : self.jump_time,
         "jump_max_speed" : self.jump_max_speed,
         "jump_length" : self.jump_length}

@dataclass
class TrainingData:
    training_id : int
    skater_id : int
    training_date : datetime
    dot_id : str
    training_jumps : List[str]

    def to_dict(self):
        return {"skater_id" : self.skater_id,
         "training_date" : self.training_date,
         "dot_id" : self.dot_id,
         "training_jumps" : self.training_jumps}

@dataclass
class SkaterData:
    skater_id : int
    skater_name : str

    def to_dict(self):
        return {"skater_name" : self.skater_name}

class DatabaseManager:
    def __init__(self):
        cred = credentials.Certificate('s2m-skating-firebase-adminsdk-3ofmb-8552d58146.json')
        try:
            firebase_admin.initialize_app(cred)
        except :
            pass
        self.db = firestore.client()
    
    def save_training_data(self, data : TrainingData) -> int:
        add_time, new_ref = self.db.collection("trainings").add(data.to_dict())
        return new_ref.id
    
    def save_jump_data(self, data : JumpData) -> int:
        add_time, new_ref = self.db.collection("jumps").add(data.to_dict())
        return new_ref.id
    
    def get_skater_from_training(self, training_id : int) -> str:
        skater_id = self.db.collection("trainings").document(training_id).get().get("skater_id")
        return skater_id
    
    def get_all_skaters(self) -> list[SkaterData]:
        data_skaters = []
        for skater in self.db.collection("skaters").stream():
            data_skaters.append(SkaterData(skater.id, skater.get("skater_name")))
        return data_skaters
    
    def set_training_date(self, training_id, date) -> None:
        self.db.collection("trainings").document(training_id).update({"training_date" : date})

    def set_current_record(self, device_id, current_record) -> None:
        self.db.collection("dots").document(device_id).update({"current_record" : firestore.ArrayUnion([current_record])})

    def get_current_record(self, deviceId) -> str:
        try:
            trainingId = self.db.collection("dots").document(deviceId).get().get("current_record")[-1]
            return trainingId
        except:
            return ""
        
    def remove_current_record(self, deviceId, trainingId):
        self.db.collection("dots").document(deviceId).update({"current_record" : firestore.ArrayRemove([trainingId])})
    
    def get_dot_from_bluetooth(self, bluetoothAddress):
        dots =  self.db.collection("dots").where(filter=firestore.firestore.FieldFilter("bluetooth_address", "==", bluetoothAddress)).get()
        if len(dots) > 0:
            return dots[0]
        else:
            return None
        
    def save_dot_data(self, deviceId : str, bluetoothAddress : str, tagName : str) -> None:
        newDot = {"bluetooth_address" : bluetoothAddress,
                  "current_record" : [],
                  "tag_name" : tagName}
        self.db.collection("dots").add(document_data=newDot, document_id=deviceId)
    
    def add_jumps_to_training(self, trainingId : str, trainingJumps : List[str]):
        self.db.collection("trainings").document(trainingId).update({"training_jumps" : trainingJumps})
    
    def findUserByEmail(self, email):
        return self.db.collection("users").where(filter=firestore.firestore.FieldFilter("email", "==", email)).get()
    
    def getAllSkaterFromCoach(self, coachId) -> List[SkaterData]:
        skatersData = []
        for skater in self.db.collection("users").document(coachId).get().get("access"):
            skatersData.append(SkaterData(skater, self.db.collection("users").document(skater).get().get("name")))
        return skatersData
