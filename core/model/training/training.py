import keras
import numpy as np
import tensorflow as tf
from sklearn.metrics import confusion_matrix

import core.model.model
import core.model.training.loader as loader


class Trainer:
    def __init__(self, dataset : loader.Dataset, model: keras.models.Model, model_filepath: str):
        self.dataset = dataset
        self.model = model

        self.loss_fn = keras.losses.CategoricalCrossentropy()  # from_logits?

        self.accuracy = tf.keras.metrics.CategoricalAccuracy()

        self.model_filepath = model_filepath

    def model_save_best(self, path):
        return keras.callbacks.ModelCheckpoint(
            path,
            monitor='val_accuracy',
            save_best_only=True,
            mode='max'
        )

    def model_load_best(self, path):
        return keras.models.load_model(path)

    def plot(self, path):
        self.plot_confusion_matrix(path)

    def plot_confusion_matrix(self, path):
        model = self.model_load_best(path)

        y_pred = model.predict({"temporal_input" : self.dataset.temporal_features_test, "scalar_input" : self.dataset.scalar_features_test})
        y_pred2 = []
        for x in y_pred:
            y_pred2.append(np.argmax(x))
        y_true = []
        for x in self.dataset.labels_test:
            y_true.append(np.argmax(x))
        results = confusion_matrix(y_true, y_pred2)
        print(results)

    def train(self, epochs: int = 100, plot: bool = True):
        """
        Do the training, and plot the confusion matrix and losses through epochs
        :param epochs:
        :param plot:
        :return: none
        """

        self.model.summary()
        try:
            trainin = self.model.fit(
                {"temporal_input" : self.dataset.temporal_features_train, "scalar_input" : self.dataset.scalar_features_train},
                self.dataset.labels_train,
                epochs=epochs,
                validation_data=self.dataset.val_dataset,
                callbacks=[self.model_save_best(self.model_filepath)],
            )
        except KeyboardInterrupt:
            self.plot(self.model_filepath)

        if plot:
            self.model = core.model.model.load_model(self.model_filepath)
            self.plot(self.model_filepath)

    def train_success(self, epochs: int = 100, plot: bool = True):
        """
        Do the training, and plot the confusion matrix and losses through epochs
        :param epochs:
        :param plot:
        :return: none
        """

        self.model.summary()
        try:
            trainin = self.model.fit(
                {"temporal_input" : self.dataset.temporal_features_train, "scalar_input" : self.dataset.scalar_features_train},
                self.dataset.labels_train,
                epochs=epochs,
                validation_data=self.dataset.val_dataset,
                callbacks=[self.model_save_best(self.model_filepath)],
                class_weight={0 : 10, 1 : 1}
            )
        except KeyboardInterrupt:
            self.plot(self.model_filepath)

        if plot:
            self.model = core.model.model.load_model(self.model_filepath)
            self.plot(self.model_filepath)