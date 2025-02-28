import argparse
import datetime
import pickle
import random
from collections import defaultdict

import joblib
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.preprocessing import image
from ultralytics import YOLO

from lib.db import get_product_info

global model
model = None
global models
models = None
MODEL_PATH = "models/YoloV8m-seg.best.pt"
class_mapping = {
    0: "carrot_carrot",
    1: "apple_red_delicious",
    2: "tomato_pink",
    3: "cucumber_long",
    4: "banana_yellow",
    5: "apple_granny",
    6: "apple_fuji",
    7: "pepper_sweet_red",
    8: "orange_orange",
    9: "onion_white",
    10: "apple_ligol",
    11: "lime_lime",
    12: "avocado_hass",
    13: "apple_golden",
    14: "kiwi_kiwi",
    15: "tomato_cherry_red",
    16: "pepper_sweet_green",
    17: "pepper_sweet_yellow",
    18: "lemon_yellow",
}

model_path = "models/best_model0228_5epochs.keras"
scaler_path = "models/scaler.pkl"


def get_cur_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_models():
    global model
    model = YOLO(MODEL_PATH)
    global models
    models = [
        (
            "Modèle 1",
            YOLO("models/Model1-YoloV8m-seg-fusionned1.pt"),
        ),
        (
            "Modèle 2",
            YOLO("models/Model2_YoloV8m-seg_fusionned.pt"),
        ),
        # ("Modèle 3", YOLO("/home/usr/code/pdufourny/balance_intelligente/models/Model3_YoloV8m-seg.pt")),
        ("Modèle origine", YOLO(MODEL_PATH)),
    ]
    print("end load_models", get_cur_time())
    return


# point d'entrée de la prediction
# get_predict(data) : point d'entrée du module, returnera les donnnées finales
#
def get_predict(data_img):
    # https://docs.ultralytics.com/reference/engine/results/#ultralytics.engine.results.Boxes
    # https://docs.ultralytics.com/reference/engine/results/#ultralytics.engine.results.Probs
    # charger le modèle
    print("start prediction")
    if model is None:
        load_models()
    # model = YOLO(MODEL_PATH)
    print("model loaded")
    results = model.predict(data_img, conf=0.1)

    result = results[0]

    res = sorted(zip(result.boxes.conf, result.boxes.cls), reverse=True)
    print("res", res)
    print("\nEnd prediction")
    item_id = int(res[0][1])
    pred = float(res[0][0])
    print("====> pred", pred)
    return item_id


# point d'entrée de la pipeline de prédiction
def process_image(img):
    print("ENTER process_image", get_cur_time())
    print("appel model_triple ", get_cur_time())
    item_id, med_conf = get_predict_triple(img)
    print("fin appel get_predict_triple ", get_cur_time())
    # item_id,med_conf = mto_predict(img)
    med_conf = round(med_conf, 2)
    print(f"======={med_conf=}")
    product_name, product_price, product_type = get_product_info(item_id)
    product_weight = str(random.choice([100, 200, 300, 500]))
    net_price = float(product_price) * float(product_weight) / 1000
    print("EXIT process_image", get_cur_time())
    return {
        "product_id": item_id,
        "product_name": product_name,
        "product_weight": product_weight,
        "product_price": product_price,
        "net_price": net_price,
        "confiance": med_conf,
    }


# modele_triple
def get_predict_triple(data_img):
    print("GP3-1")
    if model is None:
        load_models()
    # Initialisation des structures pour stocker les prédictions
    total_detections = {}
    model_detections = []
    for model_name, model_obj in models:
        print("GP3-2 : ", model_name)
        results = model_obj.predict(data_img, conf=0.5)
        model_class_counts = {}
        model_class_confidences = {}
        # Parcourir les résultats
        for result in results:
            boxes = result.boxes
            names = result.names
            for box in boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0]) * 100
                class_name = names[class_id]
                model_class_counts[class_id] = model_class_counts.get(class_id, 0) + 1
                if class_id not in model_class_confidences:
                    model_class_confidences[class_id] = []
                model_class_confidences[class_id].append(confidence)
        model_detections.append(model_class_counts)
        for class_id, count in model_class_counts.items():
            if class_id not in total_detections:
                total_detections[class_id] = []
            total_detections[class_id].extend(model_class_confidences[class_id])
    # ---- Calcul des classes majoritaires ----
    final_results = []
    for class_id, conf_list in total_detections.items():
        num_models_detected = sum(
            1 for detections in model_detections if class_id in detections
        )
        total_count = sum(
            detections.get(class_id, 0) for detections in model_detections
        )
        avg_count = round(total_count / num_models_detected)
        median_conf = np.median(conf_list)
        final_results.append((class_id, avg_count, median_conf, num_models_detected))
    # Tri des résultats : d'abord par le nombre de modèles ayant détecté l'objet, puis par le nombre moyen, puis par la confiance médiane
    final_results.sort(key=lambda x: (-x[3], -x[1], -x[2]))
    # --- Résumé des prédictions majoritaires ---
    summary_results = [
        {
            "Classe": class_id,
            "Nombre moyen": avg_count,
            "Confiance médiane": median_conf,
            "Modèles détectés": num_models_detected,
        }
        for class_id, avg_count, median_conf, num_models_detected in final_results
    ]
    # Retourne uniquement les résultats sous forme de dictionnaire
    print("summary_results", summary_results)
    if len(summary_results) == 0:
        summary_results = [{"Classe": 99}]
        summary_results = [{"Confiance médiane": 0}]

    return int(summary_results[0]["Classe"]), float(
        summary_results[0]["Confiance médiane"]
    )


####################################################################################################################

# Function to load the model
def load_model(model_path):
    model = tf.keras.models.load_model(model_path)
    print("Model loaded successfully!")
    return model


# Function to load scaler
def load_scaler(scaler_path=scaler_path):
    scaler = joblib.load(scaler_path)
    return scaler


# Function to preprocess image and structured data


def preprocess_image_and_data(img_path, scaler=None, weight=0):

    # Load scaler if not passed
    if scaler == None:
        scaler = load_scaler(scaler_path)
    # Preprocess image
    img = image.load_img(
        img_path, target_size=(224, 224)
    )  # Resize image to match model input
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    # For structured data

    num_fruits_input = np.full(
        (img_array.shape[0], 1), 0
    )  # Placeholder for continuous feature (num_fruits)

    # For weight
    if weight != 0:
        weight_input = scaler.transform([[weight]])[0][0]
    else:
        weight_input = np.full(
            (img_array.shape[0], 1), weight
        )  # Placeholder for continuous feature (weight)

    packed_input = np.full(
        (img_array.shape[0], 1), -1
    )  # Placeholder for binary feature (packed)
    crowd_input = np.full((img_array.shape[0], 1), -1)

    combined_input = [
        img_array,
        num_fruits_input,
        weight_input,
        packed_input,
        crowd_input,
    ]

    return combined_input, img


def mto_predict(img_path, weight=0):
    model = load_model(model_path)
    scaler = load_scaler(scaler_path)

    combined_input, img = preprocess_image_and_data(img_path, scaler, weight)

    predictions = model.predict(combined_input)
    print(f"{predictions=}")
    fruit_variety = predictions[0]  # Class prediction (proba)

    print(f"{fruit_variety=}")
    # fruit_count = predictions[1] # Count prediction (regression)

    # Get predicted fruit variety (class with max probability)

    predicted_fruit_type_index = np.argmax(fruit_variety, axis=1)[
        0
    ]  # Get class index with max probability
    print(f"{predicted_fruit_type_index=}")
    proba = fruit_variety[0][predicted_fruit_type_index]
    # predicted_fruit_type = class_mapping[predicted_fruit_type_index]

    # predicted_fruit_type_indices = np.argsort(fruit_variety, axis=1)[0, -2:]  # Get the indices of the two best predictions
    # predicted_fruit_type_indices = predicted_fruit_type_indices[::-1]  # Reverse to get the highest first
    # predicted_fruit_types = [class_mapping[idx] for idx in predicted_fruit_type_indices] #get class index
    # predicted_probabilities = [fruit_variety[0, idx] for idx in predicted_fruit_type_indices]

    # predicted_count_scaled = fruit_count[0][0]
    # predicted_count_not_scaled = scaler.inverse_transform([[predicted_count_scaled, 0]])[0][0]

    # return predicted_fruit_type, predicted_count_not_scaled
    return int(predicted_fruit_type_index), float(proba)
