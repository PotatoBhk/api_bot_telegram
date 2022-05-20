from db_manager import psql_product_model
from tabulate import tabulate

def test_enum():
    enums = psql_product_model.Category
    print(enums.ILUMINACION.name)

def test_generate_str_products():
    columns = ['id', 'Nombre', 'Descripción', 'Categoría', 'Código', 'Precio', 'Stock']
    data = []
    data.append((1, 'Producto 1', 'Descripción larga 1', 'Categoría 1', 'Código 1', 'Precio 1', 'Stock 1'))
    data.append((2, 'Producto 2', 'Descripción 2', 'Categoría 2', 'Código 2', 'Precio 2', 'Stock 2'))
    data.append((3, 'Producto 3', 'Descripción 3', 'Categoría 3', 'Código 3', 'Precio 3', 'Stock 3'))
    result = tabulate(data, headers=columns, tablefmt='fancy_grid')
    print(result)
    print(type(result))

def test_map_array():
    data = []
    data.append((1, 'Producto 1',  5, 'Código 1'))
    data.append((2, 'Producto 2',  6, 'Código 2'))
    data.append((3, 'Producto 3',  7, 'Código 3'))
    data.append((4, 'Producto 4',  8, 'Código 4'))  
    result = sum(map(lambda x: x[2], data))
    print("Resultado 1: ", result)
    search = list(map(lambda x: x[0] == 5, data)).index(True)
    print(list(map(lambda x: x[0] == 5, data)))
    print(search)
    # res = list(search).index(True)
    print(data)    
    data.pop(search)
    print(data)
    data2 = list(map(lambda x: x[1:4], data))
    print(data2)
    print(sum([1.1, 2.2, 3.3]))
    
test_enum()
print('============================================================')
test_generate_str_products()
print('============================================================')
test_map_array()