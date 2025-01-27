def append_list(lista1: list, lista12: list) -> list:
    lista = lista1 + lista12
    lista2 = []
    for element in lista:
        if element not in lista2:
            lista2.append(element)

    for i in range(len(lista2)):
        lista2[i] = lista2[i] ** 3
    return lista2

lista1 = [1, 2, 3, 4]
lista2 = [4, 5, 6, 7]

print(append_list(lista1, lista2))