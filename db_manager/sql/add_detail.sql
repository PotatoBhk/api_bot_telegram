INSERT INTO details (purchase_id, product_id, quantity, total) 
VALUES (%s, %s, %s, %s) RETURNING *;