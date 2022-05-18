import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

class XLSX_DB():   
    
    def __init__(self, db_path):
        self.__xls__ = pd.ExcelFile(db_path)
        
    def get_all_records(self, sheet_name):
        return pd.read_excel(self.__xls__, sheet_name)
    
    def get_record_by_param(self, sheet_name, column, value):
        df = self.get_all_records(sheet_name)
        last_id = df.tail(1).iloc[0]['#']
        return (df[df[column] == value], last_id)
    
    def get_column_names(self, sheet_name):
        df = self.get_all_records(sheet_name)
        return df.columns