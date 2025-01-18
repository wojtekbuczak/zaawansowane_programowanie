from flask import Flask, request, jsonify
import cv2
import os

app = Flask(__name__)

# pliki potrzebne do załadowania - do weryfikacji i odszukania
MODEL_PATH = "ssd_mobilenet_v3_large_coco.pb"
CONFIG_PATH = "ssd_mobilenet_v3_large_coco.pbtxt"
OUTPUT_DIR = r"C:\\do_przerzucenia\\studia\\programowanie\\person_detect"

# inicjalizacja modelu
net = cv2.dnn_DetectionModel(MODEL_PATH, CONFIG_PATH)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

@app.route("/detect", methods=["GET"])
def detect_people():
    # Get the image path from the request
    image_path = request.args.get("image_path")
    if not image_path or not os.path.exists(image_path):
        return jsonify({"error": "Image not found or path is invalid"}), 400

    # wczytanie zdjęcia
    image = cv2.imread(image_path)
    if image is None:
        return jsonify({"error": "Unable to read the image"}), 400

    # detekcja obiektów na zdjęciu
    class_ids, confidences, boxes = net.detect(image, confThreshold=0.5)

    person_count = 0
    for class_id, confidence, box in zip(class_ids.flatten(), confidences.flatten(), boxes):
        if class_id == 1: # jest to numer klasy person w coco, zrezygnowałem z pobierania całego pliku z klasami
            person_count += 1
            x, y, w, h = box
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, f"Person {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # zapis zmienionego pliku
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    output_path = os.path.join(OUTPUT_DIR, os.path.basename(image_path))
    cv2.imwrite(output_path, image)

    # Zwraca ilość wykrytych osób
    return jsonify({"detected_persons": person_count, "output_image": output_path})

if __name__ == "__main__":
    app.run(debug=True)