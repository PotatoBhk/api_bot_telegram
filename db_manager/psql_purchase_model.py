from psycopg2 import DatabaseError
from logging import Logger
import os
import re

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
            print(purchase)
            self.logger.info("Compra agregada: ", purchase)
            return purchase
        except DatabaseError as error:
            print(error)
            self.logger.error("Error al agregar compra: ", error)
            return None
        
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
        
    def get_next_id_purchase(self, db_manager):
        get_last_purchase = os.path.join(self.sql_folder, "get_purchase_last.sql")
        with open(get_last_purchase, 'r') as f:
            sql_get_last_purchase = f.read()
        try:
            cur = db_manager.cursor()
            cur.execute(sql_get_last_purchase)
            last_purchase = cur.fetchone()
            cur.close()
            if last_purchase is None:
                return "F000000001"
            print('last_purchase: ', last_purchase[0])
            return self.generate_id_purchase(last_purchase[0])
        except DatabaseError as error:
            self.logger.error("Error al obtener compra: ", error)
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
        
    def generate_id_purchase(self, last_id):
        match = re.match(r"([a-z]+)([0-9]+)", last_id, re.I)
        items = match.groups()
        nid = int(items[1]) + 1
        return items[0] + ("0" * (9-len(str(nid)))) + str(nid)