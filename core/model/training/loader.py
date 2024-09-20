import os

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from dataclasses import dataclass

import constants

@dataclass
class Dataset:
    temporal_features_train : np.array
    scalar_features_train : np.array
    labels_train : np.array
    temporal_features_test : np.array
    scalar_features_test : np.array
    labels_test : np.array
    val_dataset : tf.data.Dataset

# TODO: integrate data augmentation in the pipeline


class Loader:
    """
    This class is meant to load the data from the csv files,
    and make it ready to be used by the model for training
    """
    def __init__(self, folder_path: str, train_ratio: float = 0.8):
        assert 0 <= train_ratio <= 1

        self.folder_path = folder_path
        main_csv = os.path.join(folder_path, "jumplist.csv")
        mainFrame = pd.read_csv(main_csv)

        skaterData = pd.read_csv("data/annotated/total/skaterData.csv")

        jumps = []
        jumps_success = []
        labelstype = []
        labelssuccess = []
        fields_to_keep = constants.fields_to_keep
        self.path_jumps = []

        for index, row in mainFrame.iterrows():
            if row["success"] != 2 and row["type"] != 8:
                self.path_jumps.append(row["path"])
                jumpFrame = pd.read_csv(row['path'])
                jumpFrame = jumpFrame[fields_to_keep]

                skater_info = skaterData[skaterData["skater"] == row["skater"]][["weight","height"]].to_numpy()[0]
                jumps.append((np.nan_to_num(jumpFrame[:240].copy().to_numpy(), nan=0.0, posinf=0.0, neginf=0.0), skater_info))
                jumps_success.append((np.nan_to_num(jumpFrame[120:].copy().reset_index(drop=True).to_numpy(), nan=0.0, posinf=0.0, neginf=0.0), skater_info))
                labelstype.append(row['type'])
                labelssuccess.append(row['success'])

        # label one hot encoding
        labelEncoder = LabelEncoder()
        labelstype = np.eye(len(set(labelstype)))[labelEncoder.fit_transform(labelstype)]
        labelssuccess = np.eye(len(set(labelssuccess)))[labelEncoder.fit_transform(labelssuccess)]

        # make a training and validation dataset

        features_train, features_val, self.labels_train, self.labels_val = train_test_split(jumps, labelstype, train_size=train_ratio, shuffle=True)

        self.temporal_features_test = []
        self.scalar_features_test = []
        for x in features_val:
            self.temporal_features_test.append(x[0])
            self.scalar_features_test.append(x[1])

        self.temporal_features_train = []
        self.scalar_features_train = []
        for x in features_train:
            self.temporal_features_train.append(x[0])
            self.scalar_features_train.append(x[1])

        self.val_dataset = tf.data.Dataset.from_tensor_slices(({"temporal_input" : self.temporal_features_test, "scalar_input" : self.scalar_features_test}, self.labels_val)).batch(16)

        features_train_success, features_val_success, self.labels_train_success, self.labels_val_success = train_test_split(jumps_success, labelssuccess, train_size=train_ratio, shuffle=True)

        self.temporal_features_test_success = []
        self.scalar_features_test_success = []
        for x in features_val_success:
            self.temporal_features_test_success.append(x[0])
            self.scalar_features_test_success.append(x[1])

        self.temporal_features_train_success = []
        self.scalar_features_train_success = []
        for x in features_train_success:
            self.temporal_features_train_success.append(x[0])
            self.scalar_features_train_success.append(x[1])

        self.val_dataset_success = tf.data.Dataset.from_tensor_slices(({"temporal_input" : self.temporal_features_test_success, "scalar_input" : self.scalar_features_test_success}, self.labels_val_success)).batch(16)

    def get_type_data(self):
        data = Dataset(
            np.array(self.temporal_features_train),
            np.array(self.scalar_features_train),
            self.labels_train,
            np.array(self.temporal_features_test),
            np.array(self.scalar_features_test),
            self.labels_val,
            self.val_dataset
        )
        return data
    
    def get_success_data(self):
        data = Dataset(
            np.array(self.temporal_features_train_success),
            np.array(self.scalar_features_train_success),
            self.labels_train_success,
            np.array(self.temporal_features_test_success),
            np.array(self.scalar_features_test_success),
            self.labels_val_success,
            self.val_dataset_success
        )
        return data