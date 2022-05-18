INSERT INTO purchases (serie, client, total, state) 
VALUES (%s, %s, %s, %s) RETURNING *;