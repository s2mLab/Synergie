import copy
import os
from typing import List
import pandas as pd

import constants
from core.database.DatabaseManager import DatabaseManager, JumpData
from core.utils.jump import Jump


def mstostr(ms: float):

    s = round(ms / 1000)
    return "{:02d}:{:02d}".format(s // 60, s % 60)


def export(df: pd.DataFrame, sampleTimeFineSynchro: int = 0) -> pd.DataFrame:
    from core.data_treatment.data_generation.modelPredictor import ModelPredictor
    from core.data_treatment.data_generation.trainingSession import trainingSession
    from core.model import model
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
            jumpDictCSV.append({'videoTimeStamp': mstostr(jump.startTimestamp), 'type': predict_type[i], 'success': predict_success[i], "rotations": "{:.1f}".format(jump.rotation), "rotation_speed" : jump.max_rotation_speed, "length": jump.length})

    jumpListdf = pd.DataFrame(jumpDictCSV)
    jumpListdf = jumpListdf.sort_values(by=['videoTimeStamp'])

    return jumpListdf


def old_export():
    from core.data_treatment.data_generation.trainingSession import trainingSession
    """
    exports the data to a folder, in order to be used by the ML model
    :param folder_name: the folder where to export the data
    :param sampleTimeFineSynchro: the timefinesample of the synchro tap
    :return:
    """
    jumpList = []

    for training in os.listdir("data/new"):
        if os.path.isfile(f"data/new/{training}"):
            synchro, training_id = training.replace(".csv", "").split("_")
            synchro = int(synchro)
            skater_name = DatabaseManager().get_skater_name_from_training_id(training_id)
            df = pd.read_csv(f"data/new/{training}")

            session = trainingSession(df, synchro)

            for jump in session.jumps:
                jump_copy = copy.deepcopy(jump)
                jump_copy.skater_name = skater_name
                jump_copy.df = jump.df.copy(deep=True)
                jumpList.append(jump_copy)

    jumpDictCSV = []
    for i in jumpList:
        if i.df is None:
            continue
        jump_id = str(i.skater_name) + "_" + str(int(i.startTimestamp))
        if jump_id != "0":
            filename = os.path.join("data/pending", str(jump_id) + ".csv")
            i.generate_csv(filename)
            # since videoTimeStamp is for user input, I can change it's value to whatever I want
            jumpDictCSV.append({'path': str(jump_id) + ".csv", 'videoTimeStamp': mstostr(i.startTimestamp), 'type': i.type.value, 'skater': i.skater_name,"sucess": 2,"rotations": "{:.1f}".format(i.rotation)})

    jumpListdf = pd.DataFrame(jumpDictCSV)
    jumpListdf = jumpListdf.sort_values(by=['videoTimeStamp']).reset_index(drop=True)

    jumpListdf.to_csv("data/pending/jumplist.csv")