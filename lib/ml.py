import datetime
import pickle
import random
from collections import defaultdict

import numpy as np
from ultralytics import YOLO

from lib.db import get_product_info

global model
model = None
global models
models = None
MODEL_PATH = "/home/usr/code/pdufourny/balance_intelligente/models/YoloV8m-seg.best.pt"


def get_cur_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_models():
    global model
    model = YOLO(MODEL_PATH)
    global models
    models = [
        (
            "Modèle 1",
            YOLO(
                "/home/usr/code/pdufourny/balance_intelligente/models/model1_YoloV8m_seg_fusionned.pt"
            ),
        ),
        (
            "Modèle 2",
            YOLO(
                "/home/usr/code/pdufourny/balance_intelligente/models/Model2_YoloV8m-seg_fusionned.pt"
            ),
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
    return item_id


# point d'entrée de la pipeline de prédiction
def process_image(img):
    print("ENTER process_image", get_cur_time())
    print("appel model_triple ", get_cur_time())
    item_id = get_predict_triple(img)
    print("fin appel get_predict_triple ", get_cur_time())
    # item_id = get_predict(img)
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

    return int(summary_results[0]["Classe"])


"""
def get_predict_triple(data_img):
    print("GP3-1")
    if model is None:
        load_models()
# Initialisation des structures pour stocker les prédictions
    total_detections = {}
    model_detections = []
    for model_name, model_obj in models:
        print("GP3-2 : ",model_name)
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
                model_class_counts[class_name] = model_class_counts.get(class_name, 0) + 1
                if class_name not in model_class_confidences:
                    model_class_confidences[class_name] = []
                model_class_confidences[class_name].append(confidence)
        model_detections.append(model_class_counts)
        for class_name, count in model_class_counts.items():
            if class_name not in total_detections:
                total_detections[class_name] = []
            total_detections[class_name].extend(model_class_confidences[class_name])
# ---- Calcul des classes majoritaires ----
    final_results = []
    for class_name, conf_list in total_detections.items():
        num_models_detected = sum(1 for detections in model_detections if class_name in detections)
        total_count = sum(detections.get(class_name, 0) for detections in model_detections)
        avg_count = round(total_count / num_models_detected)
        median_conf = np.median(conf_list)
        final_results.append((class_name, avg_count, median_conf, num_models_detected))
    # Tri des résultats : d'abord par le nombre de modèles ayant détecté l'objet, puis par le nombre moyen, puis par la confiance médiane
    final_results.sort(key=lambda x: (-x[3], -x[1], -x[2]))
    # --- Résumé des prédictions majoritaires ---
    summary_results = [
        {"Classe": class_name, "Nombre moyen": avg_count, "Confiance médiane": median_conf, "Modèles détectés": num_models_detected}
        for class_name, avg_count, median_conf, num_models_detected in final_results
    ]
    # Retourne uniquement les résultats sous forme de dictionnaire
    print("summary_results",summary_results)
    return summary_results
"""
