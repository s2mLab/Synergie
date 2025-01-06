# AIOnIce

A figure skating jump recognition software using IMU data as input. 
Une application de reconnaissance des figures de patinage artistique utilisant les données de capteurs IMU

CLI usage: 

```sh
pip install requirements.txt
```

Vous aurez aussi besoin du movelladot_pc_sdk : (https://www.movella.com/support/software-documentation)

## Application

Une application avec une interface graphique disponible
```sh
python app.py
```

L'application contient : 
- Une page de connexion
- Une page d'accueil 
- des pages pop-up lors des actions de l'utilisateur

Avant d'afficher à la page d'accueil l'application cherche tous les capteurs disponibles et se connectent à ceci via Bluetooth ET USB.

Le lancement d'un enregistrement se fait en débranchant un capteur et l'arrêt de cet enregistrement en rebranchant le capteur.
Lors de ces étapes des fenêtres de confirmation s'ouvrent pour proposer des choix à l'utilisateur.

Lors de l'arrêt ou via le button sur la page d'accueil on peut exporter les données des capteurs connectés via USB. Cette opération peut prendre un certain temps et nécessite de laisser le capteur branché.
Les données brutes sont sauvegardés dans des fichiers rangés par date et sont automatiquement traités par l'application pour détecter les sauts et reconnaître les figures effectués durant l'entraînement, ces données traités sont stockés sur un base de données Firebase.

## Base de donnés

L'application utilise une base de données Firebase pour stockés les données traitées par l'application

## Entraînement des modèles

```sh
python3 main.py -t <"model_type">
```

model_type peut être "type" ou "success" entraînant respectivement la reconnaissance des figures et des chutes.
Le nombre d'époques d'entraînement doit être fixé manuellement dans `main.py`.

## Le jeu de données

Le modèle actuel a été entraîné avec un jeu de données d'environ 1500 sauts annotés.
Pour des questions de propriété privée ce jeu de données n'est pas public.

Ce jeu de données peut être entraînés avec de nouvelles données, en utilisant par exemple les données brutes stockés à chaque entraînement pour les annoter manuellement.

```sh
python3 main.py -p <"path">
```

This command will process a training file to get the jumps file, and a list of them in order to help during annotation

## Credits

Réalisé par le S2M pour Patinage Quebec.
