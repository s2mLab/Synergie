import os
import sys

import numpy as np
import pandas as pd

from keras_tuner import BayesianOptimization
import keras

import constants
from core.data_treatment.data_generation.exporter import export, old_export
from core.database.DatabaseManager import DatabaseManager, JumpData
from core.model import model
from core.model.training.loader import Loader

def main():
    """
    argv inputs:
    -p: 1331/1414/1304/1404/1128: the session to export
    -t: type/success: train the model
    -test: 1331/1414/1304/1404/1128: the session to compare with annotated one
    """

    if len(sys.argv) == 1:
        print("usage: -p <session> -t <train>")
        return

    if "-p" in sys.argv:  # export
        session_name = sys.argv[sys.argv.index("-p") + 1]
        session = constants.sessions[session_name]
        if session is None:
            raise Exception("session not found")
        old_export(session["path"], session["sample_time_fine_synchro"])

    if "-t" in sys.argv:  # train
        train_name = sys.argv[sys.argv.index("-t") + 1]
        if not (train_name in ["type","success"]):
            raise Exception("train choice not found")
        path = "data/annotated/total/"
        if train_name == "type":
            dataset = Loader(path).get_type_data()
            trainer = training.Trainer(dataset, model.transformer(dropout=0.3, mlp_dropout=0.1), constants.modeltype_filepath)
            trainer.train(epochs=10)
        elif train_name == "success":
            dataset = Loader(path).get_success_data()
            trainer = training.Trainer(dataset, model.lstm(), constants.modelsuccess_filepath)
            trainer.train_success(epochs=20)

    if "-repredict" in sys.argv:
        db_manager = DatabaseManager()
        for day in os.listdir("data/raw"):
            print(day)
            for training in os.listdir(f"data/raw/{day}"):
                training_id = training.replace(".csv", "").split("_")[1]
                df = export(df)
                trainingJumps = []
                unknow_rotation = []
                db_manager.add_jumps_to_training(training_id, trainingJumps)
                for iter,row in df.iterrows():
                    jump_time_min, jump_time_sec = row["videoTimeStamp"].split(":")
                    jump_time = '{:02d}:{:02d}'.format(int(jump_time_min), int(jump_time_sec))
                    val_rot = float(row["rotations"])
                    if val_rot >= 0.5:
                        if row["type"] != 5:
                            val_rot = np.ceil(val_rot)
                        else:
                            val_rot = np.ceil(val_rot-0.5)+0.5
                        jump_data = JumpData(0, training_id, constants.jumpType(int(row["type"])).name, val_rot, bool(row["success"]), jump_time, float(row["rotation_speed"]), float(row["length"]))
                        trainingJumps.append(jump_data.to_dict())
                    else:
                        jump_data = JumpData(0, training_id, constants.jumpType(int(row["type"])).name, 0, bool(row["success"]), jump_time, float(row["rotation_speed"]), float(row["length"]))
                        unknow_rotation.append(jump_data)
                if trainingJumps != []:
                    db_manager.add_jumps_to_training(training_id, trainingJumps)
                else:
                    for jump in unknow_rotation:
                        trainingJumps.append(jump.to_dict())
                    db_manager.add_jumps_to_training(training_id, trainingJumps)
    
    if "-rep" in sys.argv:
        for session in constants.sessions.values():
            old_export(session["path"], session["sample_time_fine_synchro"])

    if "-np" in sys.argv:
        old_export()

    if "-h" in sys.argv:
        path = "data/annotated/total/"
        dataset = Loader(path).get_type_data()
        tuner = BayesianOptimization(
            model.transformerTraining,
            objective='val_accuracy',
            max_trials=10,
            directory='hptrain',
            project_name="transformer_tuning"
        )
        tuner.search(dataset.features_train, dataset.labels_train, epochs=50, validation_data=(dataset.features_test, dataset.labels_test))
        
        best_model = tuner.get_best_models(num_models=1)[0]
        path="core/model/saved_models/checkpoint"
        keras.saving.save_model(best_model, path, overwrite=True)

        # Afficher les meilleurs hyperparamètres trouvés
        best_hyperparameters = tuner.get_best_hyperparameters(num_trials=1)[0]
        print("Meilleurs hyperparamètres:", best_hyperparameters.values)


    if "-hsuccess" in sys.argv:
        path = "data/annotated/total/"
        dataset = Loader(path).get_success_data()
        tuner = BayesianOptimization(
            model.lstm,
            objective='val_accuracy',
            max_trials=10,
            directory='hptrainsuccess',
            project_name="transformer_tuning",
        )
        tuner.search(dataset.features_train, dataset.labels_train, epochs=50, validation_data=(dataset.features_test, dataset.labels_test), class_weight={0 : 10, 1 : 1})

        best_model = tuner.get_best_models(num_models=1)[0]
        path="core/model/saved_models/success"
        keras.saving.save_model(best_model, path, overwrite=True)

        # Afficher les meilleurs hyperparamètres trouvés
        best_hyperparameters = tuner.get_best_hyperparameters(num_trials=1)[0]
        print("Meilleurs hyperparamètres:", best_hyperparameters.values)

if __name__ == "__main__":
    main()
