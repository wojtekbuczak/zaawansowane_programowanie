import csv
import time


def read_tasks():
    """Funkcja odczytująca wszystkie zadania z pliku"""
    tasks = []
    with open('tasks.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            tasks.append(row)
    return tasks


def update_task_status(task_description, new_status):
    """Aktualizuje status zadania w pliku"""
    tasks = read_tasks()
    with open('tasks.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for task in tasks:
            if task[0] == task_description:
                writer.writerow([task[0], new_status])  # Zmieniamy status zadania
            else:
                writer.writerow(task)  # Pozostawiamy inne zadania bez zmian


def consume_task(task_description):
    """Symuluje wykonanie zadania"""
    print(f"Started working on task: {task_description}")
    time.sleep(30)  # Wykonanie pracy trwa 30 sekund
    update_task_status(task_description, 'done')  # Po zakończeniu zmiana statusu na "done"
    print(f"Task '{task_description}' completed.")


if __name__ == "__main__":
    while True:
        tasks = read_tasks()

        # Szukamy zadania o statusie "pending"
        for task in tasks:
            if task[1] == 'pending':
                update_task_status(task[0], 'in_progress')  # Zmieniamy status na "in_progress"
                consume_task(task[0])  # Wykonujemy zadanie

        print("No tasks to consume. Checking again in 5 seconds...")
        time.sleep(5)  # Sprawdzaj co 5 sekund
