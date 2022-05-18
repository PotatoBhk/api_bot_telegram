import pandas as pd
import os
import re
from xlsxwriter import Workbook
from db_manager import xlst_db

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

root = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(root, 'db_manager/db_source/db.xlsx')
db_path = os.path.realpath(db_path)

def test_db_excel():
    db = xlst_db.XLSX_DB(db_path)
    records = db.get_all_records('Productos')
    print(records.iloc[2:8, 1:4])
    print('length: ', len(records))
    print(records.tail(1).iloc[0]['#'])

def filter_by_param():
    db = xlst_db.XLSX_DB(db_path)
    result = db.get_record_by_param('Productos', 'Código', 'DBD987654')
    record = result[0]
    print(record)
    print(type(record.iloc[0]['Precio']))
    print(record.columns)

def test_list():
    pedidos = {}
    pedidos['1105335002']=[('1', 'ABCD123', 'Ejemplo 1')]
    pedidos['1105335002'].append(('2', 'EFGH456', 'Ejemplo 2'))
    pedidos['1105335003']=[('3', 'ABCD124', 'Ejemplo 3')]
    pedidos['1105335003'].append(('4', 'EFGH457', 'Ejemplo 4'))
    print(pedidos['1105335002'])
    print('=========================')
    print(pedidos['1105335003'])
    print('=========================')
    print(pedidos)
    print('=========================')
    pedidos.pop('1105335002')
    print(pedidos)
    
def test_split():
    match = re.match(r"([a-z]+)([0-9]+)", 'foofo21', re.I)
    if match:
        items = match.groups()
        print(items)
    num = int('0000000009')
    print(num)

def write_to_excel():
    df = pd.DataFrame(columns=['#', 'Codigo', 'Nombre', 'Categoria', 'Descripcion', 'Precio'])
    df.loc[0] = ['1', 'ABCD123', 'Ejemplo 6', 'Electrónica', 'Descripción ejemplo 6','1.00']
    df.loc[1] = ['2', 'EFGH456', 'Ejemplo 7', 'Electrónica', 'Descripción ejemplo 7','2.00']
    df.loc[2] = ['3', 'ABCD124', 'Ejemplo 8', 'Electrónica', 'Descripción ejemplo 8','3.00']
    df.loc[3] = ['4', 'EFGH457', 'Ejemplo 9', 'Electrónica', 'Descripción ejemplo 9','4.00']
    df.to_excel(db_path, sheet_name='Productos')
  
test_db_excel()
print("=====================================")
filter_by_param()
print("=====================================")
test_list()
print("=====================================")
test_split()
print("=====================================")
write_to_excel()