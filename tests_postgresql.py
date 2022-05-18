from db_manager import psql_product_model

def test_enum():
    enums = psql_product_model.Category
    print(enums.ILUMINACION.name)
    
test_enum()