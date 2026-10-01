import tkinter as tk
from tkinter import messagebox, ttk

from pharmacy_management_system import (
    Category,
    Customer,
    Medicine,
    Supplier,
    ValidationError,
    create_sample_pharmacy,
    format_money,
)


class PharmacyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System")
        self.root.geometry("1180x760")
        self.root.minsize(1020, 680)

        self.pharmacy = create_sample_pharmacy()
        self.sale_items = []
        self.category_lookup = {}
        self.supplier_lookup = {}
        self.customer_lookup = {}
        self.medicine_lookup = {}
        self.stat_vars = {}

        self.setup_style()
        self.create_layout()
        self.refresh_all()

    def setup_style(self):
        self.colors = {
            "bg": "#eef2f5",
            "panel": "#ffffff",
            "text": "#1f2933",
            "muted": "#6b7280",
        }
        self.root.configure(bg=self.colors["bg"])

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("Panel.TFrame", background=self.colors["panel"])
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["text"], font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=self.colors["panel"], foreground=self.colors["text"], font=("Segoe UI", 10))
        style.configure("TNotebook.Tab", padding=(16, 9), font=("Segoe UI", 10))
        style.configure("Treeview", rowheight=29, font=("Segoe UI", 10), background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e5eaf0")
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), background=self.colors["bg"], foreground=self.colors["text"])
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), background=self.colors["bg"], foreground=self.colors["muted"])
        style.configure("CardTitle.TLabel", font=("Segoe UI", 9, "bold"), background=self.colors["panel"], foreground=self.colors["muted"])
        style.configure("CardValue.TLabel", font=("Segoe UI", 18, "bold"), background=self.colors["panel"], foreground=self.colors["text"])
        style.configure("Section.TLabel", font=("Segoe UI", 12, "bold"), background=self.colors["bg"], foreground=self.colors["text"])
        style.configure("TButton", padding=(10, 6))
        style.configure("Primary.TButton", padding=(12, 7), font=("Segoe UI", 10, "bold"))

    def create_layout(self):
        header = ttk.Frame(self.root, padding=(16, 14))
        header.pack(fill="x")
        title_box = ttk.Frame(header)
        title_box.pack(side="left")
        ttk.Label(title_box, text="Pharmacy Management System", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_box, text="Inventory, sales, alerts, and reports", style="Subtitle.TLabel").pack(anchor="w")
        ttk.Button(header, text="Refresh", command=lambda: self.refresh_all("Data refreshed")).pack(side="right")

        stats = ttk.Frame(self.root, padding=(16, 0, 16, 12))
        stats.pack(fill="x")
        for key, label in (("medicines", "Medicines"), ("customers", "Customers"), ("sales", "Sales"), ("revenue", "Revenue"), ("low_stock", "Low Stock"), ("expired", "Expired")):
            self.stat_vars[key] = tk.StringVar(value="0")
            self.create_stat_card(stats, label, self.stat_vars[key]).pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self.inventory_tab = ttk.Frame(self.notebook, padding=12)
        self.medicine_tab = ttk.Frame(self.notebook, padding=12)
        self.people_tab = ttk.Frame(self.notebook, padding=12)
        self.sales_tab = ttk.Frame(self.notebook, padding=12)
        self.report_tab = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.inventory_tab, text="Inventory")
        self.notebook.add(self.medicine_tab, text="Medicines")
        self.notebook.add(self.people_tab, text="Categories & People")
        self.notebook.add(self.sales_tab, text="Sales")
        self.notebook.add(self.report_tab, text="Reports")

        self.create_inventory_tab()
        self.create_medicine_tab()
        self.create_people_tab()
        self.create_sales_tab()
        self.create_report_tab()

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, anchor="w", padding=(16, 6), style="Subtitle.TLabel").pack(fill="x")

    def create_stat_card(self, parent, title, value_var):
        card = ttk.Frame(parent, style="Panel.TFrame", padding=(14, 10))
        ttk.Label(card, text=title.upper(), style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(card, textvariable=value_var, style="CardValue.TLabel").pack(anchor="w")
        return card
    def create_inventory_tab(self):
        search_frame = ttk.LabelFrame(self.inventory_tab, text="Search and Filters", padding=10)
        search_frame.pack(fill="x")

        ttk.Label(search_frame, text="Search").grid(row=0, column=0, sticky="w")
        self.search_entry = ttk.Entry(search_frame, width=36)
        self.search_entry.grid(row=0, column=1, padx=8, sticky="w")

        ttk.Button(search_frame, text="By Name", command=self.search_by_name).grid(row=0, column=2, padx=4)
        ttk.Button(search_frame, text="By ID", command=self.search_by_id).grid(row=0, column=3, padx=4)
        ttk.Button(search_frame, text="By Category", command=self.search_by_category).grid(row=0, column=4, padx=4)
        ttk.Button(search_frame, text="All", command=self.refresh_inventory).grid(row=0, column=5, padx=4)

        filters = ttk.Frame(search_frame)
        filters.grid(row=1, column=0, columnspan=6, sticky="w", pady=(10, 0))
        ttk.Button(filters, text="Available", command=self.show_available).pack(side="left", padx=(0, 6))
        ttk.Button(filters, text="Out of Stock", command=self.show_out_of_stock).pack(side="left", padx=6)
        ttk.Button(filters, text="Low Stock", command=self.show_low_stock).pack(side="left", padx=6)
        ttk.Button(filters, text="Expired", command=self.show_expired).pack(side="left", padx=6)
        ttk.Button(filters, text="Expiring Soon", command=self.show_expiring_soon).pack(side="left", padx=6)
        ttk.Button(filters, text="Active", command=self.show_active).pack(side="left", padx=6)
        ttk.Button(filters, text="Inactive", command=self.show_inactive).pack(side="left", padx=6)

        self.inventory_tree = self.create_tree(
            self.inventory_tab,
            ("id", "name", "category", "price", "quantity", "expires", "supplier", "status"),
            ("ID", "Name", "Category", "Price", "Qty", "Expires", "Supplier", "Status"),
        )
        self.inventory_tree.pack(fill="both", expand=True, pady=(12, 0))

    def create_medicine_tab(self):
        form = ttk.LabelFrame(self.medicine_tab, text="Add or Update Medicine", padding=12)
        form.pack(fill="x")

        self.med_id = self.add_labeled_entry(form, "Medicine ID", 0, 0)
        self.med_name = self.add_labeled_entry(form, "Name", 0, 2)
        self.med_price = self.add_labeled_entry(form, "Price", 1, 0)
        self.med_quantity = self.add_labeled_entry(form, "Quantity", 1, 2)
        self.med_expiration = self.add_labeled_entry(form, "Expiration YYYY-MM-DD", 2, 0)

        ttk.Label(form, text="Category").grid(row=2, column=2, sticky="w", pady=6)
        self.med_category = ttk.Combobox(form, state="readonly", width=28)
        self.med_category.grid(row=2, column=3, sticky="w", padx=8, pady=6)

        ttk.Label(form, text="Supplier").grid(row=3, column=0, sticky="w", pady=6)
        self.med_supplier = ttk.Combobox(form, state="readonly", width=28)
        self.med_supplier.grid(row=3, column=1, sticky="w", padx=8, pady=6)

        self.med_active = tk.BooleanVar(value=True)
        ttk.Checkbutton(form, text="Active", variable=self.med_active).grid(row=3, column=2, sticky="w")

        actions = ttk.Frame(form)
        actions.grid(row=4, column=0, columnspan=4, sticky="w", pady=(10, 0))
        ttk.Button(actions, text="Add Medicine", command=self.add_medicine).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Update Medicine", command=self.update_medicine).pack(side="left", padx=8)
        ttk.Button(actions, text="Delete Medicine", command=self.delete_medicine).pack(side="left", padx=8)
        ttk.Button(actions, text="Clear", command=self.clear_medicine_form).pack(side="left", padx=8)

        self.medicine_tree = self.create_tree(
            self.medicine_tab,
            ("id", "name", "category", "price", "quantity", "expires", "supplier", "status"),
            ("ID", "Name", "Category", "Price", "Qty", "Expires", "Supplier", "Status"),
        )
        self.medicine_tree.pack(fill="both", expand=True, pady=(12, 0))
        self.medicine_tree.bind("<<TreeviewSelect>>", self.load_selected_medicine)

    def create_people_tab(self):
        left = ttk.Frame(self.people_tab)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right = ttk.Frame(self.people_tab)
        right.pack(side="right", fill="both", expand=True, padx=(8, 0))

        category_form = ttk.LabelFrame(left, text="Category", padding=12)
        category_form.pack(fill="x")
        self.category_id = self.add_labeled_entry(category_form, "Category ID", 0, 0)
        self.category_name = self.add_labeled_entry(category_form, "Name", 1, 0)
        self.category_description = self.add_labeled_entry(category_form, "Description", 2, 0)
        category_actions = ttk.Frame(category_form)
        category_actions.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Button(category_actions, text="Add", command=self.add_category).pack(side="left", padx=(0, 6))
        ttk.Button(category_actions, text="Update", command=self.update_category).pack(side="left", padx=6)
        ttk.Button(category_actions, text="Delete", command=self.delete_category).pack(side="left", padx=6)

        self.category_tree = self.create_tree(left, ("id", "name", "description"), ("ID", "Name", "Description"), height=8)
        self.category_tree.pack(fill="both", expand=True, pady=(10, 0))
        self.category_tree.bind("<<TreeviewSelect>>", self.load_selected_category)

        customer_form = ttk.LabelFrame(left, text="Customer", padding=12)
        customer_form.pack(fill="x", pady=(12, 0))
        self.customer_id = self.add_labeled_entry(customer_form, "Customer ID", 0, 0)
        self.customer_name = self.add_labeled_entry(customer_form, "Name", 1, 0)
        self.customer_phone = self.add_labeled_entry(customer_form, "Phone", 2, 0)
        customer_actions = ttk.Frame(customer_form)
        customer_actions.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Button(customer_actions, text="Add", command=self.add_customer).pack(side="left", padx=(0, 6))
        ttk.Button(customer_actions, text="Update", command=self.update_customer).pack(side="left", padx=6)
        ttk.Button(customer_actions, text="Delete", command=self.delete_customer).pack(side="left", padx=6)

        self.customer_tree = self.create_tree(left, ("id", "name", "phone"), ("ID", "Name", "Phone"), height=7)
        self.customer_tree.pack(fill="both", expand=True, pady=(10, 0))
        self.customer_tree.bind("<<TreeviewSelect>>", self.load_selected_customer)

        supplier_form = ttk.LabelFrame(right, text="Supplier", padding=12)
        supplier_form.pack(fill="x")
        self.supplier_id = self.add_labeled_entry(supplier_form, "Supplier ID", 0, 0)
        self.supplier_name = self.add_labeled_entry(supplier_form, "Name", 1, 0)
        self.supplier_phone = self.add_labeled_entry(supplier_form, "Phone", 2, 0)
        self.supplier_email = self.add_labeled_entry(supplier_form, "Email", 3, 0)
        self.supplier_address = self.add_labeled_entry(supplier_form, "Address", 4, 0)
        supplier_actions = ttk.Frame(supplier_form)
        supplier_actions.grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Button(supplier_actions, text="Add", command=self.add_supplier).pack(side="left", padx=(0, 6))
        ttk.Button(supplier_actions, text="Update", command=self.update_supplier).pack(side="left", padx=6)
        ttk.Button(supplier_actions, text="Delete", command=self.delete_supplier).pack(side="left", padx=6)

        self.supplier_tree = self.create_tree(
            right,
            ("id", "name", "phone", "email", "address"),
            ("ID", "Name", "Phone", "Email", "Address"),
            height=12,
        )
        self.supplier_tree.pack(fill="both", expand=True, pady=(10, 0))
        self.supplier_tree.bind("<<TreeviewSelect>>", self.load_selected_supplier)

    def create_sales_tab(self):
        form = ttk.LabelFrame(self.sales_tab, text="Record Sale", padding=12)
        form.pack(fill="x")
        self.sale_id = self.add_labeled_entry(form, "Sale ID", 0, 0)

        ttk.Label(form, text="Customer").grid(row=0, column=2, sticky="w", pady=6)
        self.sale_customer = ttk.Combobox(form, state="readonly", width=30)
        self.sale_customer.grid(row=0, column=3, sticky="w", padx=8, pady=6)

        ttk.Label(form, text="Medicine").grid(row=1, column=0, sticky="w", pady=6)
        self.sale_medicine = ttk.Combobox(form, state="readonly", width=30)
        self.sale_medicine.grid(row=1, column=1, sticky="w", padx=8, pady=6)
        self.sale_quantity = self.add_labeled_entry(form, "Quantity", 1, 2)

        actions = ttk.Frame(form)
        actions.grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0))
        ttk.Button(actions, text="Add Item", command=self.add_sale_item).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Remove Selected Item", command=self.remove_sale_item).pack(side="left", padx=8)
        ttk.Button(actions, text="Record Sale", command=self.record_sale).pack(side="left", padx=8)
        ttk.Button(actions, text="Clear Sale", command=self.clear_sale_form).pack(side="left", padx=8)

        self.sale_item_tree = self.create_tree(
            self.sales_tab,
            ("medicine_id", "name", "quantity", "unit_price", "subtotal"),
            ("Medicine ID", "Name", "Qty", "Unit Price", "Subtotal"),
            height=8,
        )
        self.sale_item_tree.pack(fill="x", pady=(12, 0))

        ttk.Label(self.sales_tab, text="Recorded Sales", style="Section.TLabel").pack(anchor="w", pady=(16, 6))
        self.sales_tree = self.create_tree(
            self.sales_tab,
            ("id", "customer", "date", "items", "total"),
            ("Sale ID", "Customer", "Date", "Items", "Total"),
        )
        self.sales_tree.pack(fill="both", expand=True)

    def create_report_tab(self):
        actions = ttk.Frame(self.report_tab)
        actions.pack(fill="x")
        ttk.Button(actions, text="Sales Report", command=self.show_sales_report).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Low Stock Report", command=self.show_low_stock_report).pack(side="left", padx=8)
        ttk.Button(actions, text="Expiration Report", command=self.show_expiration_report).pack(side="left", padx=8)
        self.report_text = tk.Text(self.report_tab, wrap="word", height=20, font=("Consolas", 10))
        self.report_text.pack(fill="both", expand=True, pady=(12, 0))

    def create_tree(self, parent, columns, headings, height=12):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=height)
        for column, heading in zip(columns, headings):
            tree.heading(column, text=heading)
            tree.column(column, width=120, anchor="w")
        return tree

    def add_labeled_entry(self, parent, label, row, column):
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", pady=6)
        entry = ttk.Entry(parent, width=30)
        entry.grid(row=row, column=column + 1, sticky="w", padx=8, pady=6)
        return entry

    def refresh_all(self, status=None):
        self.refresh_lookups()
        self.refresh_inventory()
        self.refresh_medicine_table()
        self.refresh_category_table()
        self.refresh_supplier_table()
        self.refresh_customer_table()
        self.refresh_sales_table()
        self.refresh_sale_items_table()
        self.refresh_stats()
        self.show_sales_report()
        if status:
            self.set_status(status)

    def refresh_stats(self):
        total_revenue = sum(sale.total_price for sale in self.pharmacy.sales.values())
        self.stat_vars["medicines"].set(str(len(self.pharmacy.medicines)))
        self.stat_vars["customers"].set(str(len(self.pharmacy.customers)))
        self.stat_vars["sales"].set(str(len(self.pharmacy.sales)))
        self.stat_vars["revenue"].set(format_money(total_revenue))
        self.stat_vars["low_stock"].set(str(len(self.pharmacy.show_low_stock())))
        self.stat_vars["expired"].set(str(len(self.pharmacy.show_expired_medicines())))

    def refresh_lookups(self):
        self.category_lookup = {f"{c.category_id} - {c.name}": c for c in self.pharmacy.view_categories()}
        self.supplier_lookup = {f"{s.supplier_id} - {s.name}": s for s in self.pharmacy.view_suppliers()}
        self.customer_lookup = {f"{c.customer_id} - {c.name}": c for c in self.pharmacy.view_customers()}
        self.medicine_lookup = {f"{m.medicine_id} - {m.name}": m for m in self.pharmacy.view_medicines()}

        self.med_category["values"] = list(self.category_lookup.keys())
        self.med_supplier["values"] = list(self.supplier_lookup.keys())
        self.sale_customer["values"] = list(self.customer_lookup.keys())
        self.sale_medicine["values"] = list(self.medicine_lookup.keys())

    def medicine_row(self, medicine):
        status = "Active" if medicine.active else "Inactive"
        return (
            medicine.medicine_id,
            medicine.name,
            medicine.category.name,
            format_money(medicine.price),
            medicine.quantity,
            medicine.expiration_date,
            medicine.supplier.name,
            status,
        )

    def fill_tree(self, tree, rows):
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=row)

    def refresh_inventory(self):
        self.fill_tree(self.inventory_tree, [self.medicine_row(m) for m in self.pharmacy.show_inventory()])

    def refresh_medicine_table(self):
        self.fill_tree(self.medicine_tree, [self.medicine_row(m) for m in self.pharmacy.view_medicines()])

    def refresh_category_table(self):
        self.fill_tree(self.category_tree, [(c.category_id, c.name, c.description) for c in self.pharmacy.view_categories()])

    def refresh_supplier_table(self):
        self.fill_tree(self.supplier_tree, [(s.supplier_id, s.name, s.phone, s.email, s.address) for s in self.pharmacy.view_suppliers()])

    def refresh_customer_table(self):
        self.fill_tree(self.customer_tree, [(c.customer_id, c.name, c.phone) for c in self.pharmacy.view_customers()])

    def refresh_sales_table(self):
        rows = [(s.sale_id, s.customer.name, s.date, s.total_items(), format_money(s.total_price)) for s in self.pharmacy.sales.values()]
        self.fill_tree(self.sales_tree, rows)

    def refresh_sale_items_table(self):
        rows = []
        for medicine_id, quantity in self.sale_items:
            medicine = self.pharmacy.medicines[medicine_id]
            rows.append((medicine.medicine_id, medicine.name, quantity, format_money(medicine.price), format_money(medicine.price * quantity)))
        self.fill_tree(self.sale_item_tree, rows)

    def set_entry(self, entry, value):
        entry.delete(0, "end")
        entry.insert(0, str(value))

    def set_status(self, message):
        if hasattr(self, "status_var"):
            self.status_var.set(message)
    def selected_id(self, tree):
        selection = tree.selection()
        if not selection:
            return None
        values = tree.item(selection[0], "values")
        return values[0] if values else None

    def selected_lookup_value(self, lookup, combobox, label):
        value = combobox.get()
        if value not in lookup:
            raise ValidationError(f"Error: Please choose a valid {label}.")
        return lookup[value]

    def handle_action(self, action, success_message):
        try:
            action()
            self.refresh_all()
            messagebox.showinfo("Success", success_message)
        except ValidationError as error:
            messagebox.showerror("Validation Error", str(error))
        except Exception as error:
            messagebox.showerror("Error", f"Unexpected error: {error}")

    def search_by_name(self):
        results = self.pharmacy.search_medicine(name=self.search_entry.get())
        self.fill_tree(self.inventory_tree, [self.medicine_row(m) for m in results])

    def search_by_id(self):
        results = self.pharmacy.search_medicine(medicine_id=self.search_entry.get())
        self.fill_tree(self.inventory_tree, [self.medicine_row(m) for m in results])

    def search_by_category(self):
        results = self.pharmacy.search_medicine(category=self.search_entry.get())
        self.fill_tree(self.inventory_tree, [self.medicine_row(m) for m in results])

    def show_available(self):
        self.fill_tree(self.inventory_tree, [self.medicine_row(m) for m in self.pharmacy.filter_available_medicines()])

    def show_out_of_stock(self):
        self.fill_tree(self.inventory_tree, [self.medicine_row(m) for m in self.pharmacy.filter_out_of_stock_medicines()])

    def show_low_stock(self):
        self.fill_tree(self.inventory_tree, [self.medicine_row(m) for m in self.pharmacy.show_low_stock()])

    def show_expired(self):
        self.fill_tree(self.inventory_tree, [self.medicine_row(m) for m in self.pharmacy.show_expired_medicines()])

    def show_expiring_soon(self):
        self.fill_tree(self.inventory_tree, [self.medicine_row(m) for m in self.pharmacy.show_expiring_soon()])

    def show_active(self):
        self.fill_tree(self.inventory_tree, [self.medicine_row(m) for m in self.pharmacy.filter_active_medicines()])

    def show_inactive(self):
        self.fill_tree(self.inventory_tree, [self.medicine_row(m) for m in self.pharmacy.filter_inactive_medicines()])

    def add_medicine(self):
        def action():
            category = self.selected_lookup_value(self.category_lookup, self.med_category, "category")
            supplier = self.selected_lookup_value(self.supplier_lookup, self.med_supplier, "supplier")
            medicine = Medicine(self.med_id.get(), self.med_name.get(), category, self.med_price.get(), self.med_quantity.get(), self.med_expiration.get(), supplier, self.med_active.get())
            self.pharmacy.add_medicine(medicine)
            self.clear_medicine_form()
        self.handle_action(action, "Medicine added successfully.")

    def update_medicine(self):
        def action():
            category = self.selected_lookup_value(self.category_lookup, self.med_category, "category")
            supplier = self.selected_lookup_value(self.supplier_lookup, self.med_supplier, "supplier")
            self.pharmacy.update_medicine(self.med_id.get(), name=self.med_name.get(), category=category, price=self.med_price.get(), quantity=self.med_quantity.get(), expiration_date=self.med_expiration.get(), supplier=supplier, active=self.med_active.get())
        self.handle_action(action, "Medicine updated successfully.")

    def delete_medicine(self):
        medicine_id = self.med_id.get() or self.selected_id(self.medicine_tree)
        def action():
            if not medicine_id:
                raise ValidationError("Error: Please choose a medicine to delete.")
            self.pharmacy.delete_medicine(medicine_id)
            self.clear_medicine_form()
        self.handle_action(action, "Medicine deleted successfully.")

    def load_selected_medicine(self, event=None):
        medicine_id = self.selected_id(self.medicine_tree)
        if not medicine_id:
            return
        medicine = self.pharmacy.medicines[medicine_id]
        self.set_entry(self.med_id, medicine.medicine_id)
        self.set_entry(self.med_name, medicine.name)
        self.set_entry(self.med_price, medicine.price)
        self.set_entry(self.med_quantity, medicine.quantity)
        self.set_entry(self.med_expiration, medicine.expiration_date)
        self.med_active.set(medicine.active)
        self.med_category.set(f"{medicine.category.category_id} - {medicine.category.name}")
        self.med_supplier.set(f"{medicine.supplier.supplier_id} - {medicine.supplier.name}")

    def clear_medicine_form(self):
        for entry in (self.med_id, self.med_name, self.med_price, self.med_quantity, self.med_expiration):
            self.set_entry(entry, "")
        self.med_active.set(True)
        self.med_category.set("")
        self.med_supplier.set("")

    def add_category(self):
        self.handle_action(lambda: self.pharmacy.add_category(Category(self.category_id.get(), self.category_name.get(), self.category_description.get())), "Category added successfully.")

    def update_category(self):
        self.handle_action(lambda: self.pharmacy.update_category(self.category_id.get(), self.category_name.get(), self.category_description.get()), "Category updated successfully.")

    def delete_category(self):
        self.handle_action(lambda: self.pharmacy.delete_category(self.category_id.get()), "Category deleted successfully.")

    def load_selected_category(self, event=None):
        category_id = self.selected_id(self.category_tree)
        if category_id:
            category = self.pharmacy.categories[category_id]
            self.set_entry(self.category_id, category.category_id)
            self.set_entry(self.category_name, category.name)
            self.set_entry(self.category_description, category.description)

    def add_supplier(self):
        self.handle_action(lambda: self.pharmacy.add_supplier(Supplier(self.supplier_id.get(), self.supplier_name.get(), self.supplier_phone.get(), self.supplier_email.get(), self.supplier_address.get())), "Supplier added successfully.")

    def update_supplier(self):
        self.handle_action(lambda: self.pharmacy.update_supplier(self.supplier_id.get(), self.supplier_name.get(), self.supplier_phone.get(), self.supplier_email.get(), self.supplier_address.get()), "Supplier updated successfully.")

    def delete_supplier(self):
        self.handle_action(lambda: self.pharmacy.delete_supplier(self.supplier_id.get()), "Supplier deleted successfully.")

    def load_selected_supplier(self, event=None):
        supplier_id = self.selected_id(self.supplier_tree)
        if supplier_id:
            supplier = self.pharmacy.suppliers[supplier_id]
            self.set_entry(self.supplier_id, supplier.supplier_id)
            self.set_entry(self.supplier_name, supplier.name)
            self.set_entry(self.supplier_phone, supplier.phone)
            self.set_entry(self.supplier_email, supplier.email)
            self.set_entry(self.supplier_address, supplier.address)

    def add_customer(self):
        self.handle_action(lambda: self.pharmacy.add_customer(Customer(self.customer_id.get(), self.customer_name.get(), self.customer_phone.get())), "Customer added successfully.")

    def update_customer(self):
        self.handle_action(lambda: self.pharmacy.update_customer(self.customer_id.get(), self.customer_name.get(), self.customer_phone.get()), "Customer updated successfully.")

    def delete_customer(self):
        self.handle_action(lambda: self.pharmacy.delete_customer(self.customer_id.get()), "Customer deleted successfully.")

    def load_selected_customer(self, event=None):
        customer_id = self.selected_id(self.customer_tree)
        if customer_id:
            customer = self.pharmacy.customers[customer_id]
            self.set_entry(self.customer_id, customer.customer_id)
            self.set_entry(self.customer_name, customer.name)
            self.set_entry(self.customer_phone, customer.phone)

    def add_sale_item(self):
        try:
            medicine = self.selected_lookup_value(self.medicine_lookup, self.sale_medicine, "medicine")
            quantity = int(self.sale_quantity.get())
            if quantity <= 0:
                raise ValidationError("Error: Sale quantity must be greater than zero.")
            self.sale_items.append((medicine.medicine_id, quantity))
            self.refresh_sale_items_table()
            self.set_entry(self.sale_quantity, "")
        except ValueError:
            messagebox.showerror("Validation Error", "Error: Invalid quantity.")
        except ValidationError as error:
            messagebox.showerror("Validation Error", str(error))

    def remove_sale_item(self):
        selection = self.sale_item_tree.selection()
        if selection:
            index = self.sale_item_tree.index(selection[0])
            del self.sale_items[index]
            self.refresh_sale_items_table()

    def record_sale(self):
        try:
            customer = self.selected_lookup_value(self.customer_lookup, self.sale_customer, "customer")
            sale = self.pharmacy.create_sale(self.sale_id.get(), customer.customer_id, self.sale_items)
            self.clear_sale_form()
            self.refresh_all()
            messagebox.showinfo("Sale Recorded", sale.display_info())
        except ValidationError as error:
            messagebox.showerror("Validation Error", str(error))
        except Exception as error:
            messagebox.showerror("Error", f"Unexpected error: {error}")

    def clear_sale_form(self):
        self.set_entry(self.sale_id, "")
        self.sale_customer.set("")
        self.sale_medicine.set("")
        self.set_entry(self.sale_quantity, "")
        self.sale_items = []
        self.refresh_sale_items_table()

    def show_sales_report(self):
        self.set_report_text(self.pharmacy.generate_sales_report())

    def show_low_stock_report(self):
        lines = ["========== LOW STOCK ALERTS =========="]
        low_stock = self.pharmacy.show_low_stock()
        if not low_stock:
            lines.append("No low-stock medicines.")
        for medicine in low_stock:
            lines.append("LOW STOCK ALERT")
            lines.append(f"{medicine.name} - Only {medicine.quantity} units remaining")
        self.set_report_text("\n".join(lines))

    def show_expiration_report(self):
        lines = ["========== EXPIRATION REPORT ==========" , "", "Expired Medicines:"]
        expired = self.pharmacy.show_expired_medicines()
        if not expired:
            lines.append("No expired medicines.")
        for medicine in expired:
            lines.append(f"- {medicine.name} - Expired: {medicine.expiration_date}")
        lines.extend(["", "Expiring Soon:"])
        expiring_soon = self.pharmacy.show_expiring_soon()
        if not expiring_soon:
            lines.append("No medicines expiring soon.")
        for medicine in expiring_soon:
            lines.append(f"- {medicine.name} - Expires: {medicine.expiration_date}")
        self.set_report_text("\n".join(lines))

    def set_report_text(self, text):
        self.report_text.delete("1.0", "end")
        self.report_text.insert("1.0", text)


def main():
    root = tk.Tk()
    PharmacyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()




