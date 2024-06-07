import copy
import os
import pandas as pd

import constants
from core.data_treatment.data_generation.modelPredictor import ModelPredictor
from core.data_treatment.data_generation.trainingSession import trainingSession
from core.database.DatabaseManager import JumpData
from core.model import model


def mstostr(ms: float):

    s = round(ms / 1000)
    return "{:02d}:{:02d}".format(s // 60, s % 60)


def export(folder: str, sampleTimeFineSynchro: int = 0) -> int:
    """
    exports the data to a folder, in order to be used by the ML model
    :param folder_name: the folder where to export the data
    :param sampleTimeFineSynchro: the timefinesample of the synchro tap
    :return:
    """

    saving_path = "data/processed/"

    if not os.path.exists(saving_path):
        os.makedirs(saving_path)

    # get the list of csv files

    jumpList = []
    predict_jump = []
    skater_name = folder.split("/")[-1].split('_')[0]

    if folder.endswith(".csv"):

        session = trainingSession(folder, sampleTimeFineSynchro)

        for jump in session.jumps:
            jump_copy = copy.deepcopy(jump)
            jump_copy.skater_name = skater_name
            jump_copy.session_name = folder.split('/')[-1]
            jump_copy.df = jump.df.copy(deep=True)
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
            jumpDictCSV.append({'videoTimeStamp': mstostr(jump.startTimestamp), 'type': predict_type[i], 'success': predict_success[i], 'skater_name': jump.skater_name, "rotations": "{:.1f}".format(jump.rotation), "length": jump.length})

    filename = folder.split('/')[-1].split('_')[0]
    jumpListdf = pd.DataFrame(jumpDictCSV)
    jumpListdf = jumpListdf.sort_values(by=['videoTimeStamp'])
    jumpListdf.to_csv(os.path.join(saving_path, f"{filename}_jumplist.csv"), index=False)

    return (int(skater_name),jumpListdf)

def old_export(folder_name: str, sampleTimeFineSynchro: int = 0):
    """
    exports the data to a folder, in order to be used by the ML model
    :param folder_name: the folder where to export the data
    :param sampleTimeFineSynchro: the timefinesample of the synchro tap
    :return:
    """

    folder_name = f"data/raw/{folder_name}"
    
    saving_path = f"data/pending/{folder_name}"

    if not os.path.exists(saving_path):
        os.makedirs(saving_path)

    # get the list of csv files

    jumpList = []

    for file in os.listdir(folder_name):
        if file.endswith(".csv"):

            print(os.path.join(folder_name, file))
            session = trainingSession(os.path.join(folder_name, file), sampleTimeFineSynchro)
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
            jumpDictCSV.append({'path': str(jump_id) + ".csv", 'videoTimeStamp': mstostr(i.startTimestamp), 'type': i.type.value, 'skater_name': i.skater_name, "rotations": "{:.1f}".format(i.rotation), "length": i.length})

    jumpListdf = pd.DataFrame(jumpDictCSV)
    jumpListdf = jumpListdf.sort_values(by=['videoTimeStamp'])
    jumpListdf.to_csv(os.path.join(saving_path, "jumplist.csv"), index=False)