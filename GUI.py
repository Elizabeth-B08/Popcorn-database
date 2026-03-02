import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import csv
from datetime import datetime

DB_NAME = "store.db"

# -----------------------------
# DATABASE SETUP
# -----------------------------

CREATE_PRODUCT_TABLE = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    supplier_id INTEGER,
    timestamp TEXT
);
"""

CREATE_SUPPLIER_TABLE = """
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INTEGER PRIMARY KEY,
    supplier_name TEXT,
    address TEXT,
    phone TEXT
);
"""


def connect():
    return sqlite3.connect(DB_NAME)


def create_tables():
    with connect() as conn:
        conn.execute(CREATE_PRODUCT_TABLE)
        conn.execute(CREATE_SUPPLIER_TABLE)


def add_supplier_column_if_missing():
    with connect() as conn:
        try:
            conn.execute("ALTER TABLE products ADD COLUMN supplier_id INTEGER")
        except sqlite3.OperationalError:
            pass

def add_timestamp_column_if_missing():
    with connect() as conn:
        try:
            conn.execute("ALTER TABLE products ADD COLUMN timestamp TEXT")
        except sqlite3.OperationalError:
            pass

# -----------------------------
# PRODUCT FUNCTIONS
# -----------------------------

def add_product(name, price, quantity, supplier_id, use_timestamp=True):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if use_timestamp else ""
    with connect() as conn:
        conn.execute(
            "INSERT INTO products (name, price, quantity, supplier_id, timestamp) VALUES (?, ?, ?, ?, ?)",
            (name, price, quantity, supplier_id, timestamp)
        )


def get_products(sort_by="name", order="ASC"):
    valid_columns = ["name", "price", "quantity"]
    valid_order = ["ASC", "DESC"]

    if sort_by not in valid_columns:
        sort_by = "name"
    if order not in valid_order:
        order = "ASC"

    query = f"SELECT * FROM products ORDER BY {sort_by} {order}"

    with connect() as conn:
        return conn.execute(query).fetchall()


def delete_product(product_id):
    with connect() as conn:
        conn.execute("DELETE FROM products WHERE id=?", (product_id,))



# SUPPLIER FUNCTIONS


def populate_suppliers():
    suppliers = [
        (1, "Popcorn Co", "123 Corn St", "111-222-3333"),
        (2, "Snack World", "456 Butter Ave", "444-555-6666"),
        (3, "Cinema Snacks Ltd", "789 Movie Rd", "777-888-9999")
    ]
    with connect() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO suppliers VALUES (?, ?, ?, ?)", suppliers
        )


def get_supplier_info(supplier_id):
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM suppliers WHERE supplier_id=?",
            (supplier_id,)
        ).fetchone()



# CSV FEATURES


def import_from_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return

    try:
        with open(file_path, newline="") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                add_product(row[0], float(row[1]), int(row[2]), int(row[3]), timestamp_var.get())

        refresh_list()
        messagebox.showinfo("Success", "Products imported successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Import failed:\n{e}")


def backup_to_csv():
    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with connect() as conn:
        data = conn.execute("SELECT * FROM products").fetchall()

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Name", "Price", "Quantity", "Supplier ID", "Timestamp"])
        writer.writerows(data)

    messagebox.showinfo("Backup Complete", f"Database backed up as {filename}")



# GUI FUNCTIONS


def refresh_list():
    listbox.delete(0, tk.END)
    for product in get_products(sort_var.get(), order_var.get()):
        display_text = f"ID:{product[0]} | {product[1]} | ${product[2]:.2f} | Qty:{product[3]} | Supplier:{product[4]}"
        listbox.insert(tk.END, display_text)


def add_button_clicked():
    try:
        name = name_entry.get().strip()
        price = float(price_entry.get())
        quantity = int(quantity_entry.get())
        supplier_id = int(supplier_entry.get())

        if not name:
            raise ValueError

        if not get_supplier_info(supplier_id):
            messagebox.showerror("Error", "Supplier ID does not exist.")
            return

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid values.")
        return

    add_product(name, price, quantity, supplier_id, timestamp_var.get())
    clear_entries()
    refresh_list()


def delete_button_clicked():
    selected = listbox.curselection()
    if not selected:
        return

    item_text = listbox.get(selected[0])
    product_id = int(item_text.split("|")[0].replace("ID:", "").strip())
    delete_product(product_id)
    refresh_list()


def show_supplier_info():
    selected = listbox.curselection()
    if not selected:
        return

    item_text = listbox.get(selected[0])
    supplier_id = int(item_text.split("Supplier:")[1].strip())
    supplier = get_supplier_info(supplier_id)

    if supplier:
        messagebox.showinfo(
            "Supplier Info",
            f"Name: {supplier[1]}\nAddress: {supplier[2]}\nPhone: {supplier[3]}"
        )


def clear_entries():
    name_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)
    supplier_entry.delete(0, tk.END)


def change_font_color():
    color = colorchooser.askcolor()[1]
    if color:
        listbox.config(fg=color)


# GUI SETUP


create_tables()
add_supplier_column_if_missing()
add_timestamp_column_if_missing()
populate_suppliers()

root = tk.Tk()
root.title("Popcorn Store Management")
root.geometry("750x600")

timestamp_var = tk.BooleanVar(value=True)

# Menu
menu = tk.Menu(root)
settings_menu = tk.Menu(menu, tearoff=0)
settings_menu.add_checkbutton(label="Timestamp On/Off", variable=timestamp_var)
settings_menu.add_command(label="Change Font Color", command=change_font_color)
settings_menu.add_command(label="Import From CSV", command=import_from_csv)
settings_menu.add_command(label="Backup To CSV", command=backup_to_csv)
menu.add_cascade(label="Settings", menu=settings_menu)
root.config(menu=menu)

# Layout Frame
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Product Name").grid(row=0, column=0)
name_entry = tk.Entry(frame)
name_entry.grid(row=0, column=1)

tk.Label(frame, text="Price").grid(row=1, column=0)
price_entry = tk.Entry(frame)
price_entry.grid(row=1, column=1)

tk.Label(frame, text="Quantity").grid(row=2, column=0)
quantity_entry = tk.Entry(frame)
quantity_entry.grid(row=2, column=1)

tk.Label(frame, text="Supplier ID").grid(row=3, column=0)
supplier_entry = tk.Entry(frame)
supplier_entry.grid(row=3, column=1)

tk.Button(frame, text="Add Product", command=add_button_clicked).grid(row=4, columnspan=2, pady=5)

# Sorting
sort_var = tk.StringVar(value="name")
order_var = tk.StringVar(value="ASC")

tk.OptionMenu(root, sort_var, "name", "price", "quantity").pack()
tk.OptionMenu(root, order_var, "ASC", "DESC").pack()
tk.Button(root, text="Apply Sort", command=refresh_list).pack(pady=5)

# Listbox
listbox = tk.Listbox(root, width=100)
listbox.pack(pady=10)

tk.Button(root, text="Delete Selected", command=delete_button_clicked).pack()
tk.Button(root, text="View Supplier Info", command=show_supplier_info).pack()

refresh_list()
root.mainloop()