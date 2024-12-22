from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


def odczytaj_tekst_z_obrazu(sciezka_do_obrazu):

    try:
        obraz = Image.open(sciezka_do_obrazu)
        tekst = pytesseract.image_to_string(obraz, lang='pol')
        return tekst
    except Exception as e:
        return f"Błąd podczas przetwarzania obrazu: {e}"


sciezka = ("obrazy\\retro.png")
wynik = odczytaj_tekst_z_obrazu(sciezka)
print("Odczytany tekst:")
print(wynik)