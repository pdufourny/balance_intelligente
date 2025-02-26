import pickle
from collections import defaultdict

from ultralytics import YOLO

MODEL_PATH = "/home/usr/code/pdufourny/balance_intelligente/models/YoloV8m-seg.best.pt"


def get_product_info(item_id):
    product_name = ("nouveau produit",)
    product_weight = ("0.51",)
    product_price = ("15€",)
    return product_name, product_weight, product_price


# point d'entrée de la prediction
# gt_predict(data) : point d'entrée du module, returnera les donnnées finales
#
def get_predict(data_img):
    # https://docs.ultralytics.com/reference/engine/results/#ultralytics.engine.results.Boxes
    # https://docs.ultralytics.com/reference/engine/results/#ultralytics.engine.results.Probs
    # charger le modèle
    print("start predction")
    model = YOLO(MODEL_PATH)
    results = model.predict(data_img, conf=0.1)

    probs = []
    for result in results:
        for box in result.boxes:
            probs.append(box.conf.item())  # Convert tensor to Python float
    # confiance = int(box[0].conf.item())   # confiance
    item_id = int(box[0].cls.item())  # class num
    print("item:", item_id)
    print("Probabilities:", probs)

    # print(results[0].names)

    print("\nEnd prediction")

    return item_id


# point d'entrée de la pipeline de prédiction
def process_image(img):
    print("inside process_image")
    item_id = str(get_predict(img))
    product_name, product_weight, product_price = get_product_info(item_id)

    return {
        "product_id": item_id,
        "product_name": product_name,
        "product_weight": product_weight,
        "product_price": product_price,
    }


def get_class_item(item_idx):
    pass
