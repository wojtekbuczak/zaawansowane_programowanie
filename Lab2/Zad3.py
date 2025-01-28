def check_parity(liczba):
    if (liczba % 2) == 0:
        parity = True
    else:
        parity = False
    return parity


liczba = int(input("Podaj licbe:"))
if check_parity(liczba):
    print("Liczba parzysta")
else:
    print("Liczba nieparzysta")
