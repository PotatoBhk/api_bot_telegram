INSERT INTO products (code, name, price, description, category_id) 
VALUES (%s, %s, %s, %s, %s) RETURNING *;