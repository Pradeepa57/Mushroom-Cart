import sqlite3

conn = sqlite3.connect("mushroom_cart.db")
cursor = conn.cursor()

print("Users:")
for row in cursor.execute("SELECT * FROM users"):
    print(row)

print("\nProducts:")
for row in cursor.execute("SELECT * FROM products"):
    print(row)

print("\nOrders:")
for row in cursor.execute("SELECT * FROM orders"):
    print(row)

conn.close()
