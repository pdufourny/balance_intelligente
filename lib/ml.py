import pickle

import pandas as pd


# point d'entrée de la prediction
# gt_predict(data) : point d'entrée du module, returnera les donnnées finales
#
def get_predict(data):
    # charger le modèle
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
    # effectuer la prediction
    prediction = model.predict(data)
    return prediction


# point d'entrée de la pipeline de prédiction
def predict(data):

    return 2  # classe de produit 2 , phse de test


def get_class_item(item_idx):
    pass
