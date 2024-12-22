def wyswietl_co_drugi_element(lista_liczb):
    for i in range(0, len(lista_liczb), 2):
        print(lista_liczb[i])

lista_liczb_10 = [32,12,65,23,69,44,1,7,31,100]

wyswietl_co_drugi_element(lista_liczb_10)
print("Wycinanie listy: ")
print(lista_liczb_10[::2])

