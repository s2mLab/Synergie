# AIOnIce

A figure skating jump recognition software using IMU data as input. 

CLI usage: 

```sh
pip install requirements.txt
```

You also need to get the movelladot-pc-sdk : check (https://www.movella.com/support/software-documentation)

## App

An app with a visual interface is available, you can launch it with
```sh
python app.py
```

It contains three main pages:
- A management page for adding and deleting skaters
- A stats page for checking previous training and their contents
- A scan page to look for captors and start/stop record of training

The record of a training can also be launch by disconnecting (usb wired) a captor, the app will ask for starting a new training.
When a captor is pluged via usb to the computer, the app will stop a record if there is one and will export the data contains in the captors, next it will erase the memory of the captor (Beware! Erasing the memory take around 1 minute).
The data exported is on a csv file stock in ```data/new```, the app will automatically detect a new file and will process it with the models to predicts jumps, their types and their success.

## Database

The app use a firestore database to stock data.

## Training the models

```sh
python3 main.py -t <"model_type">
```

-t is used for training.
model_type can be "type" or "success" respectively training the recognition of jumps and their success

## About the dataset

Current model has been trained with a dataset of roughly 1000 annotated jumps.
Because of privacy concerns, the dataset is not disclosed.

This dataset can be extend with new data, in order to do this, you need to use :

```sh
python3 main.py -p <"path">
```

This command will process a training file to get the jumps file, and a list of them in order to help during annotation

## Credits

Made by the S2M for Patinage Quebec.
