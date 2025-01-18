import csv
import time

def add_task(task_description):
    with open('tasks.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([task_description, 'pending'])  # Dodajemy nową pracę z statusem "pending"
        print(f"Task '{task_description}' added with status 'pending'.")

if __name__ == "__main__":
    task_description = input("Enter task description: ")
    add_task(task_description)
