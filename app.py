from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # required for session handling

# ---------------- Database Connection ----------------
def get_db_connection():
    conn = sqlite3.connect("mushroom_cart.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- Routes ----------------
@app.route("/")
def home():
    return "Welcome to Mushroom Cart!"


@app.route("/adduser")
def add_user():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, password, usertype) VALUES (?, ?, ?, ?)",
                   ("Ravi Kumar", "ravi@example.com", "12345", "farmer"))
    conn.commit()
    conn.close()
    return "Sample user added!"


@app.route("/addproduct", methods=["GET", "POST"])
def add_product():
    if "farmer_id" not in session:
        return "Please login as farmer first!"

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        quantity = request.form["quantity"]
        image = request.form["image"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, quantity, image, farmer_id) VALUES (?, ?, ?, ?, ?)",
                       (name, price, quantity, image, session["farmer_id"]))
        conn.commit()
        conn.close()

        return "Product added successfully!"
    return render_template("add_product.html")


@app.route("/getproducts")
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    return str([dict(row) for row in rows])


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        usertype = request.form["usertype"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password, usertype) VALUES (?, ?, ?, ?)",
                       (name, email, password, usertype))
        conn.commit()
        conn.close()

        return "Farmer registered successfully!"
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ? AND usertype = 'farmer'",
                       (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
           session["farmer_id"] = user["user_id"]
           return render_template("farmer_dashboard.html", name=user["name"])
        else:
            return "Invalid email or password!"
    return render_template("login.html")


@app.route("/myproducts")
def my_products():
    if "farmer_id" not in session:
        return "Please login as farmer first!"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE farmer_id = ?", (session["farmer_id"],))
    products = cursor.fetchall()
    conn.close()

    return render_template("view_products.html", products=products)


@app.route("/buyer_register", methods=["GET", "POST"])
def buyer_register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        usertype = request.form["usertype"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password, usertype) VALUES (?, ?, ?, ?)",
                       (name, email, password, usertype))
        conn.commit()
        conn.close()

        return "Buyer registered successfully!"
    return render_template("buyer_register.html")


@app.route("/buyer_login", methods=["GET", "POST"])
def buyer_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ? AND usertype = 'buyer'",
                       (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
          session["buyer_id"] = user["user_id"]
          return render_template("buyer_dashboard.html", name=user["name"])
        else:
            return "Invalid email or password!"
    return render_template("buyer_login.html")


@app.route("/browse")
def browse_products():
    if "buyer_id" not in session:
        return "Please login as buyer first!"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    return render_template("browse_products.html", products=products)


@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    if "buyer_id" not in session:
        return "Please login as buyer first!"

    qty = int(request.form["qty"])

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if not product:
        return "Product not found!"

    # initialize cart if not present
    if "cart" not in session:
        session["cart"] = []

    # add product to cart
    session["cart"].append({
        "id": product["product_id"],
        "name": product["name"],
        "price": float(product["price"]),
        "qty": qty
    })

    session.modified = True   # 🔴 important line

    return redirect("/cart")


@app.route("/cart")
def view_cart():
    if "buyer_id" not in session:
        return "Please login as buyer first!"

    cart = session.get("cart", [])
    return render_template("view_cart.html", cart=cart)


@app.route("/place_order", methods=["POST"])
def place_order():
    if "buyer_id" not in session:
        return "Please login as buyer first!"

    cart = session.get("cart", [])
    if not cart:
        return "Your cart is empty!"

    conn = get_db_connection()
    cursor = conn.cursor()

    for item in cart:
        cursor.execute("INSERT INTO orders (buyer_id, product_id, quantity) VALUES (?, ?, ?)",
                       (session["buyer_id"], item["id"], item["qty"]))
        cursor.execute("UPDATE products SET quantity = quantity - ? WHERE product_id = ?",
                       (item["qty"], item["id"]))

    conn.commit()
    conn.close()
    session["cart"] = []

    return "Order placed successfully!"


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email == "admin@mushroom.com" and password == "admin123":
            session["admin"] = True
            return "Welcome Admin!"
        else:
            return "Invalid admin credentials!"
    return render_template("admin_login.html")


@app.route("/admin/users")
def admin_users():
    if "admin" not in session:
        return "Please login as admin first!"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    return render_template("view_users.html", users=users)


@app.route("/admin/products")
def admin_products():
    if "admin" not in session:
        return "Please login as admin first!"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    return render_template("view_all_products.html", products=products)


@app.route("/admin/orders")
def admin_orders():
    if "admin" not in session:
        return "Please login as admin first!"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    conn.close()

    return render_template("view_orders.html", orders=orders)

@app.route("/home")
def home_page():
    return render_template("home.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

