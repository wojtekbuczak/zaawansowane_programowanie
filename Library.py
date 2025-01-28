class Library:
    def __init__(self, city, street, zip_code, open_hours, phone):
        self.city = city
        self.street = street
        self.zip_code = zip_code
        self.open_hours = str(open_hours)
        self.phone = phone

    def __str__(self):
        return f"Biblioteka z miastem {self.city} ulica {self.street} kodem pocztowym {self.zip_code} godzinami otwarcia w formacie str {self.open_hours} i numer telefonu {self.phone}."
