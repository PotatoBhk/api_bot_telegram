from psycopg2 import DatabaseError
from logging import Logger
from enum import Enum, unique
import os

@unique
class Category(Enum):
    ILUMINACION = 1
    ELECTRONICA = 2
    TELECOMUNICACIONES = 3

class Product():
    
    def __init__(self, logger: Logger):
        root = os.path.dirname(__file__)
        self.sql_folder = os.path.realpath(os.path.join(root, "sql"))
        self.logger = logger
        self.logger.info("Iniciando clase Product...")
        
    def add_category(self, category, db_manager):
        add_category = os.path.join(self.sql_folder, "add_category.sql")
        with open(add_category, 'r') as f:
            sql_add_category = f.read()
        try:
            cur = db_manager.cursor()
            cur.execute(sql_add_category, (category,))
            result = cur.fetchone()
            db_manager.commit()    
            cur.close()
            self.logger.info("Categoría agregada: ", result)
            return True
        except DatabaseError as error:
            self.logger.error("Error al agregar categoría: ", error)
            return False
    
    def get_category(self, id, db_manager):
        get_category = os.path.join(self.sql_folder, "get_category.sql")
        with open(get_category, 'r') as f:
            sql_get_category = f.read()
        try:
            cur = db_manager.cursor()
            cur.execute(sql_get_category, (id,))
            category = cur.fetchone()   
            cur.close()
            return category
        except DatabaseError as error:
            self.logger.error("Error al obtener categoría: ", error)
            return None
    
    def get_categories(self, db_manager):
        get_categories = os.path.join(self.sql_folder, "get_categories.sql")
        with open(get_categories, 'r') as f:
            sql_get_categories = f.read()
        try:
            cur = db_manager.cursor()
            cur.execute(sql_get_categories)
            categories = cur.fetchall()
            cur.close()
            return categories
        except DatabaseError as error:
            self.logger.error("Error al obtener categorías: ", error)
            return None
    
    def add_product(self, data, db_manager):       
        add_product = os.path.join(self.sql_folder, "add_product.sql")
        with open(add_product, 'r') as f:
            sql_add_product = f.read()        
        try:            
            cur = db_manager.cursor()
            cur.execute(sql_add_product, (
                    data[0], #code
                    data[1], #name
                    data[2], #description
                    data[3], #price
                    data[4]  #category
                )
            )
            product = cur.fetchone()
            db_manager.commit()    
            cur.close()
            self.logger.info("Producto agregado: ", product)
            return True
        except DatabaseError as error:
            self.logger.error("Error al agregar producto: ", error)
            return False
        
    def get_product(self, code, db_manager):
        get_product = os.path.join(self.sql_folder, "get_product.sql")
        with open(get_product, 'r') as f:
            sql_get_product = f.read()
        try:
            cur = db_manager.cursor()
            cur.execute(sql_get_product, (code,))
            product = cur.fetchone()
            db_manager.commit()
            cur.close()
            return product
        except DatabaseError as error:
            self.logger.error("Error al obtener producto: ", error)
            return None
    
    def get_products(self, page, db_manager):
        offset = (page - 1) * 5
        get_products = os.path.join(self.sql_folder, "get_products.sql")
        with open(get_products, 'r') as f:
            sql_get_products = f.read()
        try:
            cur = db_manager.cursor()
            cur.execute(sql_get_products, (offset, 5))
            products = cur.fetchall()
            cur.close()
            return products
        except DatabaseError as error:
            self.logger.error("Error al obtener productos: ", error)
            return None
    
    def get_products_by_category(self, page, category, db_manager):
        offset = (page - 1) * 5
        get_products = os.path.join(self.sql_folder, "get_products_by_category.sql")
        with open(get_products, 'r') as f:
            sql_get_products = f.read()
        try:
            cur = db_manager.cursor()
            cur.execute(sql_get_products, (category, offset, 5))
            products = cur.fetchall()
            cur.close()
            return products
        except DatabaseError as error:
            self.logger.error("Error al obtener productos: ", error)
            return None