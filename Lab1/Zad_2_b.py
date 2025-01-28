def lista_x_2v1(lista_liczb):
    lista_liczb_x_2 = []
    for i in range(len(lista_liczb)):
        lista_liczb_x_2.insert(i, lista_liczb[i] * 2)
    return lista_liczb_x_2


def lista_x_2v2(lista_liczb):
    lista_liczb = [lista_liczb[liczba] * 2 for liczba in range(len(lista_liczb))]
    return lista_liczb


def wyswietl_liste(lista_liczb):
    for element_listy in lista_liczb:
        print(element_listy)


lista_liczb_wej = [4, 20, 1, 69, 18]

nowa_lista_a = lista_x_2v1(lista_liczb_wej)
# wyswietl_liste(nowa_lista_a)
print(nowa_lista_a)
nowa_lista_b = lista_x_2v2(lista_liczb_wej)
# wyswietl_liste(nowa_lista_b)
print(nowa_lista_b)
