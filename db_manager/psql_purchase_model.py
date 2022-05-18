from psycopg2 import DatabaseError
from logging import Logger
from enum import Enum, unique
import os

class Purchase():
    
    def __init__(self, logger: Logger):
        root = os.path.dirname(__file__)
        self.sql_folder = os.path.realpath(os.path.join(root, "sql"))
        self.logger = logger
        self.logger.info("Iniciando clase Purchase...")
    
    def add_purchase(self, data, db_manager):
        add_purchase = os.path.join(self.sql_folder, "add_purchase.sql")
        with open(add_purchase, 'r') as f:
            sql_add_purchase = f.read()
        try:
            cur = db_manager.cursor()
            cur.execute(sql_add_purchase, data)
            purchase = cur.fetchone()
            db_manager.commit()
            cur.close()
            self.logger.info("Compra agregada: ", purchase)
            return True
        except DatabaseError as error:
            self.logger.error("Error al agregar compra: ", error)
            return False
        
    def get_purchase(self, serie, db_manager):
        get_purchase = os.path.join(self.sql_folder, "get_purchase.sql")
        with open(get_purchase, 'r') as f:
            sql_get_purchase = f.read()
        try:
            cur = db_manager.cursor()
            cur.execute(sql_get_purchase, (serie,))
            purchase = cur.fetchone()
            cur.close()
            return purchase
        except DatabaseError as error:
            self.logger.error("Error al obtener compra: ", error)
            return None
        
    def get_purchases(self, db_manager):
        get_purchases = os.path.join(self.sql_folder, "get_purchases.sql")
        with open(get_purchases, 'r') as f:
            sql_get_purchases = f.read()
        try:
            cur = db_manager.cursor()
            cur.execute(sql_get_purchases)
            purchases = cur.fetchall()
            cur.close()
            return purchases
        except DatabaseError as error:
            self.logger.error("Error al obtener compras: ", error)
            return None
    
    def get_purchases_by_client(self, client_id, db_manager):
        get_purchases_by_client = os.path.join(self.sql_folder, "get_purchases_by_client.sql")
        with open(get_purchases_by_client, 'r') as f:
            sql_get_purchases_by_client = f.read()
        try:
            cur = db_manager.cursor()
            cur.execute(sql_get_purchases_by_client, (client_id,))
            purchases = cur.fetchall()
            cur.close()
            return purchases
        except DatabaseError as error:
            self.logger.error("Error al obtener compras: ", error)
            return None
    
    def add_detail(self, data, db_manager):
        add_detail = os.path.join(self.sql_folder, "add_detail.sql")
        with open(add_detail, 'r') as f:
            sql_add_detail = f.read()
        try:
            cur = db_manager.cursor()
            cur.execute(sql_add_detail, data)
            detail = cur.fetchone()
            db_manager.commit()
            cur.close()
            self.logger.info("Detalle agregado: ", detail)
            return True
        except DatabaseError as error:
            self.logger.error("Error al agregar detalle: ", error)
            return False
    
    def get_details(self, purchase_id, db_manager):
        get_details = os.path.join(self.sql_folder, "get_details.sql")
        with open(get_details, 'r') as f:
            sql_get_details = f.read()
        try:
            cur = db_manager.cursor()
            cur.execute(sql_get_details, (purchase_id,))
            details = cur.fetchall()
            cur.close()
            return details
        except DatabaseError as error:
            self.logger.error("Error al obtener detalles: ", error)
            return None