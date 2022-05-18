import psycopg2
import os
from logging import Logger

class Database():
    
    def __init__(self, logger: Logger):
        root = os.path.dirname(__file__)
        self.sql_folder = os.path.realpath(os.path.join(root, "sql"))
        self.logger = logger
        self.logger.info("Iniciando conexión con base de datos...")
        
    def init_db(self):
        try:
            #Read Schema's SQL file
            schema = os.path.join(self.sql_folder, "schema.sql")
            with open(schema, 'r') as f:
                sql_schema = f.read()
            #Initiate and connect with database   
            self.conn = psycopg2.connect(
                user = 'admin', 
                password = 'mpassword',
                database = 'telebotdb'
            )
            cur = self.conn.cursor()
            cur.execute(sql_schema)
            self.conn.commit()
            cur.close()
            self.logger.info("Base de datos inicializada...")                       
            return True
        except psycopg2.DatabaseError as error:
            self.logger.error("Error al inicializar la base de datos: ", error)
            self.conn.close()
            return False
    
    def get_connection(self):
        return self.conn
    
    def close(self):
        try:
            self.conn.close()
            self.logger.info("Conexión con base de datos terminada...")
        except psycopg2.DatabaseError as error:
            self.logger.error("Error al cerrar la conexión con la base de datos: ", error)