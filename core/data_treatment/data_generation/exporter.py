import copy
import os
from typing import List
import pandas as pd

import constants
from core.data_treatment.data_generation.modelPredictor import ModelPredictor
from core.data_treatment.data_generation.trainingSession import trainingSession
from core.database.DatabaseManager import JumpData
from core.model import model
from core.utils.jump import Jump


def mstostr(ms: float):

    s = round(ms / 1000)
    return "{:02d}:{:02d}".format(s // 60, s % 60)


def export(skater_id, df: pd.DataFrame, sampleTimeFineSynchro: int = 0) -> int:
    """
    exports the data to a folder, in order to be used by the ML model
    :param folder_name: the folder where to export the data
    :param sampleTimeFineSynchro: the timefinesample of the synchro tap
    :return:
    """
    # get the list of csv files

    jumpList : List[Jump]= []
    predict_jump = []

    session = trainingSession(df, sampleTimeFineSynchro)

    for jump in session.jumps:
        jump_copy = copy.deepcopy(jump)
        jump_copy.skater_name = skater_id
        jump_copy.df_type = jump.df_type.copy(deep=True)
        jump_copy.df_success = jump.df_success.copy(deep=True)
        jumpList.append(jump_copy)
        predict_jump.append(jump_copy.df)
        
    model_test_type = model.load_model(constants.modeltype_filepath)
    model_test_success = model.load_model(constants.modelsuccess_filepath)
    prediction = ModelPredictor(model_test_type, model_test_success)
    predict_type, predict_success = prediction.predict(predict_jump)

    jumpDictCSV = []
    for i,jump in enumerate(jumpList):
        if jump.df is None:
            continue
        if len(jump.df) == 400:
            # since videoTimeStamp is for user input, I can change it's value to whatever I want
            jumpDictCSV.append({'videoTimeStamp': mstostr(jump.startTimestamp), 'type': predict_type[i], 'success': predict_success[i], 'skater_name': jump.skater_name, "rotations": "{:.1f}".format(jump.rotation), "rotation_speed" : jump.max_rotation_speed, "length": jump.length})

    jumpListdf = pd.DataFrame(jumpDictCSV)
    jumpListdf = jumpListdf.sort_values(by=['videoTimeStamp'])

    return jumpListdf

def old_export(folder_name: str, sampleTimeFineSynchro: int = 0):
    """
    exports the data to a folder, in order to be used by the ML model
    :param folder_name: the folder where to export the data
    :param sampleTimeFineSynchro: the timefinesample of the synchro tap
    :return:
    """
    saving_path = f"data/pending/{folder_name}"

    folder_name = f"data/raw/{folder_name}"
    
    if not os.path.exists(saving_path):
        os.makedirs(saving_path)

    # get the list of csv files

    jumpList = []

    for file in os.listdir(folder_name):
        if file.endswith(".csv"):

            print(os.path.join(folder_name, file))
            df = pd.read_csv(os.path.join(folder_name, file))
            session = trainingSession(df, sampleTimeFineSynchro)
            skater_name = file.split('_')[0]

            # session.plot()

            for jump in session.jumps:
                jump_copy = copy.deepcopy(jump)
                jump_copy.skater_name = skater_name
                jump_copy.session_name = folder_name.split('/')[-1]
                jump_copy.df = jump.df.copy(deep=True)
                jumpList.append(jump_copy)
    jumpDictCSV = []
    for i in jumpList:
        if i.df is None:
            continue
        jump_id = i.session_name + "_" + i.skater_name + "_" + str(int(i.startTimestamp))
        if jump_id != "0":
            filename = os.path.join(saving_path, str(jump_id) + ".csv")
            i.generate_csv(filename)
            # since videoTimeStamp is for user input, I can change it's value to whatever I want
            jumpDictCSV.append({'path': str(jump_id) + ".csv", 'videoTimeStamp': mstostr(i.startTimestamp), 'type': i.type.value, 'skater': i.skater_name,"sucess": 2,"rotations": "{:.1f}".format(i.rotation)})

    jumpListdf = pd.DataFrame(jumpDictCSV)
    jumpListdf = jumpListdf.sort_values(by=['videoTimeStamp'])
    jumpListdf.to_csv(os.path.join(saving_path, "jumplist.csv"), index=False)