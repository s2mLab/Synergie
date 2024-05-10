import os
import sys

import constants
from core.data_treatment.data_generation.exporter import export
from core.model import model
from core.model.training import training
from core.model.training.loader import Loader
from core.data_treatment.data_generation.modelPredictor import ModelPredictor


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
        export(session["path"], session["sample_time_fine_synchro"])

    if "-t" in sys.argv:  # train
        train_name = sys.argv[sys.argv.index("-t") + 1]
        if not (train_name in ["type","success"]):
            raise Exception("train choice not found")
        path = "data/annotated/total/"
        if train_name == "type":
            dataset = Loader(path).get_type_data()
            trainer = training.Trainer(dataset, model.transformer(dropout=0.3, mlp_dropout=0.1), constants.modeltype_filepath)
            trainer.train(epochs=350)
        elif train_name == "success":
            dataset = Loader(path).get_success_data()
            trainer = training.Trainer(dataset, model.newmodel(), constants.modelsuccess_filepath)
            trainer.train(epochs=50)

    if "-test" in sys.argv:  # test
        session_name = sys.argv[sys.argv.index("-test") + 1]
        session = constants.sessions[session_name]
        path_anno = os.path.join("data/annotated/",session["path"])
        path_pend = os.path.join("data/pending/",session["path"])
        model_test_type = model.load_model(constants.modeltype_filepath)
        model_test_success = model.load_model(constants.modelsuccess_filepath)
        prediction = ModelPredictor(model_test_type, model_test_success)
        prediction.load_from_csv(path_pend)
        error_type = prediction.checktype(path_anno)
        error_success = prediction.checksuccess(path_anno)
        print(error_type)
        print(error_success)

if __name__ == "__main__":
    main()
