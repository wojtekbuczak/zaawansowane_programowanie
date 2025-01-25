from flask import Flask, request, jsonify
import cv2
import os
import pika
import uuid
import json
import requests
from threading import Thread
import asyncio
from aio_pika import connect_robust, Message, DeliveryMode, ExchangeType


app = Flask(__name__)

# Słownik do przechowywania statusów zadań
task_status = {}

# pliki potrzebne do załadowania
MODEL_PATH = "ssd_mobilenet_v3_large_coco.pb"
CONFIG_PATH = "ssd_mobilenet_v3_large_coco.pbtxt"
OUTPUT_DIR = r"C:\\do_przerzucenia\\studia\\programowanie\\person_detect"
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'image_queue'
UPLOAD_DIR = r"C:\\do_przerzucenia\\studia\\programowanie\\person_uploads"

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
            f.write(response.content)
        return image_path
    return None

# Funkcja do przetwarzania zdjęcia
def process_image(image_path, task_id):
    # Aktualizacja statusu na "in progress"
    task_status[task_id] = {
        "status": "in progress",
        "result": None
    }

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
        task_status[task_id]["status"] = "completed"
        task_status[task_id]["result"] = {"persons_detected": 0}
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

    # Aktualizacja statusu na "completed" z wynikiem
    task_status[task_id]["status"] = "completed"
    task_status[task_id]["result"] = {"persons_detected": person_count}

    return person_count

#Dodawania zadań
def send_to_queuev1(image_path, task_id):
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

            # Dodanie statusu "queued" do słownika
            task_status[task_id] = {
                "status": "queued",
                "result": None
            }

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

        # Dodanie statusu "queued" do słownika
        task_status[task_id] = {
            "status": "queued",
            "result": None
        }

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
    # Dodanie statusu "queued" do słownika
    task_status[task_id] = {
        "status": "queued",
        "result": None
    }
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

@app.route("/task_status", methods=["GET"])
def check_task_status():
    task_id = request.args.get("task_id")
    if not task_id:
        return jsonify({"error": "Task ID not provided"}), 400

    # Sprawdzanie statusu zadania
    task_info = task_status.get(task_id)
    if not task_info:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({
        "task_id": task_id,
        "status": task_info["status"],
        "result": task_info.get("result")  # Wynik może być `None`, jeśli zadanie wciąż trwa
    })

# Endpoint obsługujący przesyłanie zdjęć metodą POST
@app.route('/detect_upload', methods=['POST'])
def detect_upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Zapisanie przesłanego pliku
    if file:
        # Tworzenie unikalnego ID zadania
        task_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        saved_file_path = os.path.join(UPLOAD_DIR, f"{task_id}{file_extension}")

        # Zapisanie przesłanego pliku w katalogu
        file.save(saved_file_path)

        # Wrzucenie zadania do kolejki RabbitMQ
        send_to_queue(saved_file_path, task_id)

        # Zwrócenie informacji zwrotnej z task_id
        return jsonify({
            "message": "File has been uploaded and task has been queued.",
            "task_id": task_id
        }), 200


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

# Asynchroniczna obsługa kolejki RabbitMQ
async def process_queue():
    connection = await connect_robust(RABBITMQ_HOST)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)

        async for message in queue:
            async with message.process():
                data = json.loads(message.body)
                image_path = data["image_path"]
                task_id = data["task_id"]
                print(f"[x] Odebrano zadanie: {task_id} dla obrazu {image_path}")
                process_image(image_path, task_id)

# Dodawanie zadań
async def send_to_queue(image_path, task_id):
    connection = await connect_robust(RABBITMQ_HOST)
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            Message(
                body=json.dumps({"image_path": image_path, "task_id": task_id}).encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=QUEUE_NAME,
        )

if __name__ == "__main__":
    #from threading import Thread
    loop = asyncio.get_event_loop()
    loop.create_task(process_queue())
    # Uruchomienie przetwarzania RabbitMQ w osobnym wątku
    #rabbit_thread = Thread(target=main, daemon=True)
    #rabbit_thread.start()

    #uruchomienie serwera Flask
    app.run(debug=True)