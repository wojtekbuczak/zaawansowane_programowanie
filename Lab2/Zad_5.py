def check_list(lista: list, element: int):
    check = False
    for i in lista:
        if i == element:
            check = True
    return check


lista = [2, 5, 7, 9]
sprawdz = check_list(lista, 7)
print(sprawdz)
