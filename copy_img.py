import shutil
import os


def copy_image(image_path, output_folder, copies, prefix="test"):

    os.makedirs(output_folder, exist_ok=True)

    for i in range(2, copies + 2):  # Zaczynamy od "test2" do "test201"
        # Tworzymy nową nazwę pliku
        new_name = f"{prefix}{i}.jpg"
        new_path = os.path.join(output_folder, new_name)

        # Kopiujemy plik
        shutil.copy(image_path, new_path)
        print(f"Skopiowano jako {new_name}")


# Przykład użycia
original_image = r"C:\\do_przerzucenia\\studia\\programowanie\\person_pics\\test.jpg"  # Zamień na rzeczywistą ścieżkę
output_directory = "C:\\do_przerzucenia\\studia\\programowanie\\person_pics"  # Zamień na rzeczywistą ścieżkę
number_of_copies = 100

copy_image(original_image, output_directory, number_of_copies)