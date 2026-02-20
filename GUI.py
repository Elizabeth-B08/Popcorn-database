import sqlite3
import tkinter as tk
from tkinter import messagebox

# -----------------------------
# DATABASE FUNCTIONS
# -----------------------------

DB_NAME = "store.db"

CREATE_PRODUCT_TABLE = """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL
            )
        """

def connect():
    return sqlite3.connect(DB_NAME)

def create_table():
    with connect() as conn:
        conn.execute(CREATE_PRODUCT_TABLE)

def add_product(name, price, quantity):
    with connect() as conn:
        conn.execute(
            "INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
            (name, price, quantity)
        )

def get_products(order_by="name", direction="ASC"):
    with connect() as conn:
        return conn.execute(
            f"SELECT * FROM products ORDER BY {order_by} {direction}"
        ).fetchall()

def delete_product_by_id(product_id):
    with connect() as conn:
        conn.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,)
        )

# -----------------------------
# GUI FUNCTIONS
# -----------------------------

def refresh_list():
    listbox.delete(0, tk.END)
    for product in get_products(sort_var.get(), order_var.get()):
        listbox.insert(tk.END, product)

def add_button_clicked():
    name = name_entry.get().strip()

    try:
        price = float(price_entry.get())
        quantity = int(quantity_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Price must be a number and quantity must be an integer.")
        return

    if not name:
        messagebox.showwarning("Missing Data", "Product name is required.")
        return

    add_product(name, price, quantity)
    clear_entries()
    refresh_list()

def delete_button_clicked():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("Selection Error", "Select a product to delete.")
        return

    product = listbox.get(selected[0])
    delete_product_by_id(product[0])
    refresh_list()

def clear_entries():
    name_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)

# -----------------------------
# GUI SETUP
# -----------------------------

create_table()

root = tk.Tk()
root.title("Video Game Store Inventory")
root.geometry("520x500")

# Input Fields
tk.Label(root, text="Game Name").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Label(root, text="Price").pack()
price_entry = tk.Entry(root)
price_entry.pack()

tk.Label(root, text="Quantity").pack()
quantity_entry = tk.Entry(root)
quantity_entry.pack()

tk.Button(root, text="Add Product", command=add_button_clicked).pack(pady=5)

# Sorting Controls
sort_frame = tk.Frame(root)
sort_frame.pack(pady=5)

tk.Label(sort_frame, text="Sort By:").grid(row=0, column=0)

sort_var = tk.StringVar(value="name")
tk.OptionMenu(sort_frame, sort_var, "name", "price").grid(row=0, column=1)

order_var = tk.StringVar(value="ASC")
tk.OptionMenu(sort_frame, order_var, "ASC", "DESC").grid(row=0, column=2)

tk.Button(sort_frame, text="Apply Sort", command=refresh_list).grid(row=0, column=3)

# Product List
listbox = tk.Listbox(root, width=60)
listbox.pack(pady=10)

tk.Button(root, text="Delete Selected Product", command=delete_button_clicked).pack()

refresh_list()
root.mainloop()