from flask import Flask, request, jsonify
import cv2
import os
import pika
import uuid
import json

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

# Funkcja do przetwarzania zdjęcia
def process_image(image_path, task_id):
    print(f"[x] Przetwarzanie obrazu: {image_path} dla zadania {task_id}")

    # Próba wczytania obrazu
    image = cv2.imread(image_path)
    if image is None:
        print(f"Nie można wczytać obrazu: {image_path}")
        return

    # Detekcja obiektów na zdjęciu
    class_ids, confidences, boxes = net.detect(image, confThreshold=0.5)

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

    # Sprawdzenie, czy to folder
    if os.path.isdir(image_path):
        image_files = [
            os.path.join(image_path, file)
            for file in os.listdir(image_path)
            if file.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        if not image_files:
            return jsonify({"error": "No valid image files found in the folder"}), 400

        # Zakolejkowanie wszystkich plików w folderze
        task_ids = []
        for image_file in image_files:
            task_id = str(uuid.uuid4())
            send_to_queue(image_file, task_id)
            task_ids.append(task_id)

        return jsonify({
            "message": f"{len(task_ids)} images have been queued for processing.",
            "task_ids": task_ids
        })

    # Jeśli to plik, zakolejkuj go
    elif os.path.isfile(image_path):
        task_id = str(uuid.uuid4())
        send_to_queue(image_path, task_id)
        return jsonify({
            "message": "Image has been queued for processing.",
            "task_id": task_id
        })
    else:
        return jsonify({"error": "Invalid path"}), 400

# Obsługa wiadomości RabbitMQ
def callback(ch, method, properties, body):
    message = json.loads(body)
    image_path = message.get("image_path")
    task_id = message.get("task_id")

    if image_path and task_id:
        print(f"[x] Przetwarzanie obrazu: {image_path} dla zadania {task_id}")
        process_image(image_path, task_id)
    else:
        print("[x] Otrzymano nieprawidłową wiadomość: brak 'image_path' lub 'task_id'")

    ch.basic_ack(delivery_tag=method.delivery_tag)


# Konfiguracja RabbitMQ
def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    print(' [*] Oczekiwanie na wiadomości. Aby zakończyć, naciśnij CTRL+C.')

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    channel.start_consuming()

if __name__ == "__main__":
    from threading import Thread

    # Uruchomienie przetwarzania RabbitMQ w osobnym wątku
    rabbit_thread = Thread(target=main, daemon=True)
    rabbit_thread.start()

    #uruchomienie serwera Flask
    app.run(debug=True)