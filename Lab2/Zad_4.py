def check_digit(liczba1: int, liczba2: int, liczba3: int) -> bool:
    if (liczba1 + liczba2) >= liczba3:
        check = True
    else:
        check = False
    return check


check = check_digit(5, 4, 7)
print(check)
