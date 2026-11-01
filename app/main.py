import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "super_secret_key_for_inventory"

# Retrieve environment variables dynamically injected by Kubernetes
DB_HOST = os.environ.get("DB_HOST", "mysql-service")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "SecretPassword123")
DB_NAME = os.environ.get("DB_NAME", "inventory_db")

def get_db_connection():
    """Establishes and returns a direct connection to the MySQL pod."""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    return connection

def init_db():
    """Initializes the database schema if it doesn't already exist."""
    # Loop to wait for MySQL pod initialization inside the cluster
    for i in range(5):
        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            cursor.execute(f"USE {DB_NAME}")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sku VARCHAR(50) NOT NULL UNIQUE,
                    name VARCHAR(100) NOT NULL,
                    category VARCHAR(50),
                    quantity INT NOT NULL DEFAULT 0,
                    price DECIMAL(10, 2) NOT NULL
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print("Database initialized successfully.")
            break
        except Error as e:
            print(f"Database connection attempt {i+1} failed. Retrying in 5s...")
            time.sleep(5)

# --- ROUTES ---

@app.route('/')
def index():
    """Fetches inventory items and renders the primary operations dashboard."""
    conn = get_db_connection()
    if not conn:
        return "Database Connection Error. Please verify Kubernetes service status.", 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventory")
    items = cursor.fetchall()
    
    # Calculate live operational metrics for frontend cards
    total_value = sum(item['price'] * item['quantity'] for item in items)
    low_stock_count = sum(1 for item in items if item['quantity'] <= 5)
    
    cursor.close()
    conn.close()
    return render_template('index.html', items=items, total_value=total_value, low_stock=low_stock_count)

@app.route('/add', methods=['POST'])
def add_item():
    """Processes form submission to append a new item into MySQL."""
    sku = request.form['sku']
    name = request.form['name']
    category = request.form['category']
    quantity = int(request.form['quantity'])
    price = float(request.form['price'])
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO inventory (sku, name, category, quantity, price) VALUES (%s, %s, %s, %s, %s)",
                (sku, name, category, quantity, price)
            )
            conn.commit()
            flash("Item added successfully!", "success")
        except Error as e:
            flash(f"Error adding item: {e}", "danger")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    """Removes an inventory record dynamically via its unique identifier."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id = %s", (item_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Item removed from inventory.", "warning")
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)

