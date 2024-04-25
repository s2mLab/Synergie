import os
import keras
import constants

import numpy as np
import pandas as pd

class ModelPredictor:
    def __init__(self, datasetPath,  model_type: keras.models.Model, model_success: keras.models.Model) -> None:
        filename = "jumplist.csv"

        df_jumps = pd.read_csv(os.path.join(datasetPath, filename))
        predictType = []
        predictSuccess = []

        for index,rows in df_jumps.iterrows():
            df_onejump = pd.read_csv(os.path.join(datasetPath, rows["path"]))
            df_predictjump = df_onejump[constants.fields_to_keep]
            if len(df_predictjump) == 400:
                prediction = model_type.predict(np.array([df_predictjump]))
                predictType.append(np.argmax(prediction))
                prediction = model_success.predict(np.array([df_predictjump]))
                predictSuccess.append(np.argmax(prediction))
            else:
                predictType.append(8)
                predictSuccess.append(2)
        
        df_jumps['type'] = predictType
        df_jumps['success'] = predictSuccess

        self.df_jumps = df_jumps
        
        df_jumps.to_csv(os.path.join(datasetPath, filename), index=False)

    def checktype(self, checkPath):
        df_check = pd.read_csv(os.path.join(checkPath, "jumplist.csv"))
        typeCheck = np.array(df_check["type"])
        typePredict = np.array(self.df_jumps["type"])

        index = typeCheck!=8
        typeCheck = typeCheck[index]
        typePredict = typePredict[index]
        indexbis = typePredict!=2
        typeCheck = typeCheck[indexbis]
        typePredict = typePredict[indexbis]
        
        total = (typePredict==typeCheck).sum()/len(typeCheck)
        precision = []
        for i in range(6):
            count = (typeCheck==i).sum()
            precision.append((typePredict[typeCheck==i]==i).sum()/count)
        precision.append(total)
        return precision
    
    def checksuccess(self, checkPath):
        df_check = pd.read_csv(os.path.join(checkPath, "jumplist.csv"))
        typeCheck = np.array(df_check["success"])
        typePredict = np.array(self.df_jumps["success"])

        index = typeCheck!=2
        typeCheck = typeCheck[index]
        typePredict = typePredict[index]
        indexbis = typePredict!=2
        typeCheck = typeCheck[indexbis]
        typePredict = typePredict[indexbis]

        total = (typePredict==typeCheck).sum()/len(typeCheck)
        precision = []
        for i in range(2):
            count = (typeCheck==i).sum()
            precision.append((typePredict[typeCheck==i]==i).sum()/count)
        precision.append(total)
        return precision