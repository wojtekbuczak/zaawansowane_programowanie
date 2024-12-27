from PIL import Image
import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


def odczytaj_tekst_z_obrazu_pil(sciezka_do_obrazu):
    try:
        obraz = Image.open(sciezka_do_obrazu)
        tekst = pytesseract.image_to_string(obraz, lang='pol')
        return tekst
    except Exception as e:
        return f"Błąd podczas przetwarzania obrazu: {e}"

def odczytaj_tekst_z_obrazu_cv2(sciezka_do_obrazu):
    try:
        obraz = cv2.imread(sciezka_do_obrazu)
        tekst = pytesseract.image_to_string(obraz, lang='pol')
        return tekst
    except Exception as e:
        return f"Błąd podczas przetwarzania obrazu: {e}"


sciezka = ("obrazy\\nba1.jpg")
wynik = odczytaj_tekst_z_obrazu_cv2(sciezka)
print("Odczytany tekst:")
print(wynik)

