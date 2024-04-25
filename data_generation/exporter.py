import copy
import os

import pandas as pd

from data_generation.trainingSession import trainingSession


def mstostr(ms: float):

    s = round(ms / 1000)
    return "{:02d}:{:02d}".format(s // 60, s % 60)


def export(folder_name: str, sampleTimeFineSynchro: int = 0):
    """
    exports the data to a folder, in order to be used by the ML model
    :param folder_name: the folder where to export the data
    :param sampleTimeFineSynchro: the timefinesample of the synchro tap
    :return:
    """

    saving_path = "data/pending/"
    loading_path = "data/raw/"
    folder = os.path.join(loading_path,folder_name)

    if not os.path.exists(saving_path):
        os.makedirs(saving_path)

    # get the list of csv files

    jumpList = []

    for file in os.listdir(folder):
        if file.endswith(".csv"):

            print(os.path.join(folder, file))
            session = trainingSession(os.path.join(folder, file), sampleTimeFineSynchro)
            skater_name = file.split('_')[0]

            # session.plot()

            for jump in session.jumps:
                jump_copy = copy.deepcopy(jump)
                jump_copy.skater_name = skater_name
                jump_copy.session_name = folder.split('/')[-1]
                jump_copy.df = jump.df.copy(deep=True)
                jumpList.append(jump_copy)
    jumpDictCSV = []
    for i in jumpList:
        if i.df is None:
            continue
        jump_id = i.skater_name + "_" + str(int(i.startTimestamp)) + ".csv"
        if not os.path.exists(os.path.join(saving_path, folder_name)):
            os.makedirs(os.path.join(saving_path, folder_name))
        if jump_id != "0":
            filename = os.path.join(saving_path, folder_name, jump_id)
            i.generate_csv(filename)
            # since videoTimeStamp is for user input, I can change it's value to whatever I want
            jumpDictCSV.append({'path': jump_id, 'videoTimeStamp': mstostr(i.startTimestamp), 'type': i.type.value, 'skater_name': i.skater_name, "rotations": "{:.1f}".format(i.rotation), "length": i.length})

    jumpListdf = pd.DataFrame(jumpDictCSV)
    jumpListdf = jumpListdf.sort_values(by=['videoTimeStamp'])
    jumpListdf.to_csv(os.path.join(saving_path, folder_name, "jumplist.csv"), index=False)