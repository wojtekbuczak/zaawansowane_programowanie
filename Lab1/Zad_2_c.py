def wyswietl_liczby_parzyste(lista_liczb):
    parzyste_liczby = [liczba for liczba in range(len(lista_liczb)) if liczba % 2 == 0]
    print(parzyste_liczby)


lista_liczb_10 = [32, 12, 65, 23, 69, 44, 1, 7, 31, 100]

wyswietl_liczby_parzyste(lista_liczb_10)
