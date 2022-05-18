INSERT INTO products (code, name, description, price, category_id) 
VALUES (%s, %s, %s, %s, %s) RETURNING *;