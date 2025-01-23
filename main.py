from flask import Flask, request, jsonify
import cv2
import os
import pika
import uuid
import json
import requests
from threading import Thread


app = Flask(__name__)

# pliki potrzebne do załadowania
MODEL_PATH = "ssd_mobilenet_v3_large_coco.pb"
CONFIG_PATH = "ssd_mobilenet_v3_large_coco.pbtxt"
OUTPUT_DIR = r"C:\\do_przerzucenia\\studia\\programowanie\\person_detect"
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'image_queue'

# inicjalizacja modelu
def initialize_model():
    net = cv2.dnn_DetectionModel(MODEL_PATH, CONFIG_PATH)
    net.setInputSize(320, 320)
    net.setInputScale(1.0 / 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)
    return net

net = initialize_model()

# Funkcja do pobrania obrazu z URL
def download_image(url, task_id):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        #if not os.path.exists(OUTPUT_DIR):
        #    os.makedirs(OUTPUT_DIR)

        image_path = os.path.join(OUTPUT_DIR, f"{task_id}_downloaded_image.jpg")
        with open(image_path, 'wb') as f:
            #for chunk in response.iter_content(1024):
            #    f.write(chunk)
            f.write(response.content)
        return image_path
    return None

# Funkcja do przetwarzania zdjęcia
def process_image(image_path, task_id):
    print(f"[x] Przetwarzanie obrazu: {image_path} dla zadania {task_id}")

    # Próba wczytania obrazu
    image = cv2.imread(image_path)
    if image is None:
        print(f"Nie można wczytać obrazu: {image_path}")
        return 0

    # Detekcja obiektów na zdjęciu
    detection_result = net.detect(image, confThreshold=0.5)

    # Sprawdzanie, czy cokolwiek wykryto
    if not detection_result or len(detection_result) != 3:
        print(f"Brak detekcji na obrazie {image_path}")
        return 0

    class_ids, confidences, boxes = detection_result

    if class_ids is None or confidences is None or boxes is None:
        print(f"Brak wykrytych obiektów na obrazie {image_path}")
        return 0

    person_count = 0
    for class_id, confidence, box in zip(class_ids.flatten(), confidences.flatten(), boxes):
        if class_id == 1:  # Klasa "person" w COCO
            person_count += 1
            x, y, w, h = box
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, f"Person {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Zapis zmienionego obrazu
    output_file = os.path.join(OUTPUT_DIR, f"{task_id}_{os.path.basename(image_path)}")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    success = cv2.imwrite(output_file, image)
    if success:
        print(f"Wykryto {person_count} osoby na obrazie {image_path}. Wynik zapisano w {output_file}.")
    else:
        print(f"Nie udało się zapisać zmodyfikowanego obrazu dla {image_path}.")

    return person_count

# Endpoint do dodawania zadań
def send_to_queue(image_path, task_id):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    message = json.dumps({"image_path": image_path, "task_id": task_id})
    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2  # Ustawienie trwałości wiadomości
        )
    )

    connection.close()

@app.route("/detect", methods=["GET"])
def detect_people():
    # Pobranie ścieżki z zapytania
    image_path = request.args.get("image_path")
    if not image_path or not os.path.exists(image_path):
        return jsonify({"error": "Path not found or invalid"}), 400

    if os.path.isdir(image_path):  # Jeśli podano folder
        image_files = [
            os.path.join(image_path, file)
            for file in os.listdir(image_path)
            if file.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        if not image_files:
            return jsonify({"error": "No valid image files found in the folder"}), 400

        detection_results = []  # Lista przechowująca wyniki detekcji
        for image_file in image_files:
            task_id = str(uuid.uuid4())
            send_to_queue(image_file, task_id)

            # Proces detekcji na bieżąco
            person_count = process_image(image_file, task_id)
            detection_results.append({
                "task_id": task_id,
                "image": image_file,
                "persons_detected": person_count
            })

        return jsonify({
            "message": f"{len(detection_results)} images have been processed and queued for further processing.",
            "detection_results": detection_results
        })

    elif os.path.isfile(image_path):  # Jeśli podano plik
        task_id = str(uuid.uuid4())
        send_to_queue(image_path, task_id)

        # Proces detekcji na bieżąco
        person_count = process_image(image_path, task_id)
        return jsonify({
            "message": "Image has been processed and queued for further processing.",
            "task_id": task_id,
            "image": image_path,
            "persons_detected": person_count
        })
    else:
        return jsonify({"error": "Invalid path"}), 400

# Endpoint do obsługi obrazów z URL
@app.route("/detect_from_url", methods=["GET"])
def detect_from_url():
    image_url = request.args.get("image_url")
    if not image_url:
        return jsonify({"error": "Image URL not provided"}), 400

    task_id = str(uuid.uuid4())
    image_path = download_image(image_url, task_id)
    if not image_path:
        return jsonify({"error": "Failed to download image"}), 400

    # Wykonywanie detekcji na pobranym obrazie
    person_count = process_image(image_path, task_id)
    if person_count is None:
        return jsonify({"error": "Image processing failed"}), 500

    send_to_queue(image_path, task_id)

    return jsonify({
        "message": "Task added to queue for processing.",
        "task_id": task_id,
        "image_url": image_url,
        "persons_detected": person_count
    })

# Konfiguracja RabbitMQ
def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    print(' [*] Oczekiwanie na wiadomości. Aby zakończyć, naciśnij CTRL+C.')

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    channel.start_consuming()

# Obsługa kolejki RabbitMQ
def callback(ch, method, properties, body):
    data = json.loads(body)
    image_path = data["image_path"]
    task_id = data["task_id"]
    print(f"[x] Odebrano zadanie: {task_id} dla obrazu {image_path}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    from threading import Thread

    # Uruchomienie przetwarzania RabbitMQ w osobnym wątku
    rabbit_thread = Thread(target=main, daemon=True)
    rabbit_thread.start()

    #uruchomienie serwera Flask
    app.run(debug=True)