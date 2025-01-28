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

def odczytaj_tekst_z_obrazu_cv2(sciezka_do_obrazu, metoda_wygladzania="medianBlur"):
    try:
        obraz = cv2.imread(sciezka_do_obrazu)
        szary_obraz = cv2.cvtColor(obraz, cv2.COLOR_BGR2GRAY)

        if metoda_wygladzania == "medianBlur":
            converted_img = cv2.medianBlur(szary_obraz, 3)
        elif metoda_wygladzania == "gaussianBlur":
            converted_img = cv2.threshold(cv2.GaussianBlur(szary_obraz, (5, 5), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        elif metoda_wygladzania == "bilateralFilter":
            converted_img = cv2.threshold(cv2.bilateralFilter(szary_obraz, 5, 75, 75), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        elif metoda_wygladzania == "medianBlurThreshold":
            converted_img = cv2.threshold(cv2.medianBlur(szary_obraz, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        elif metoda_wygladzania == "adaptiveGaussianBlur":
            converted_img = cv2.adaptiveThreshold(cv2.GaussianBlur(szary_obraz, (5, 5), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
        elif metoda_wygladzania == "adaptiveBilateralFilter":
            converted_img = cv2.adaptiveThreshold(cv2.bilateralFilter(szary_obraz, 9, 75, 75), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
        elif metoda_wygladzania == "adaptiveMedianBlur":
            converted_img = cv2.adaptiveThreshold(cv2.medianBlur(szary_obraz, 3), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
        else:
            return "Nieznana metoda wygładzania"

        tekst = pytesseract.image_to_string(converted_img, lang='pol')
        return tekst
    except Exception as e:
        return f"Błąd podczas przetwarzania obrazu: {e}"

sciezka = "obrazy\\test2.jpg"
metoda = "medianBlurThreshold"  # do wyboru
wynik = odczytaj_tekst_z_obrazu_cv2(sciezka, metoda)
print("Odczytany tekst:")
print(wynik)
