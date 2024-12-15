class Employee:
    def __init__(self, first_name, last_name, hire_date, birth_date, city, street, zip_code, phone):
        self.first_name = first_name
        self.last_name = last_name
        self. hire_date = hire_date
        self.birth_date = birth_date
        self.city = city
        self.street = street
        self.zip_code = zip_code
        self.phone = phone

    def __str__(self):
        return (f'Pracownik biblioteki o imieniu//'
                f' {self.first_name} nazwisku {self.last_name} dacie zatrudnienia {self.hire_date}, //'
                f'urodzenia {self.birth_date}, oraz adresem {self.city} {self.street} {self.zip_code} i numerem telefonu//'
                f' {self.phone}.')