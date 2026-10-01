from datetime import date, datetime, timedelta
from collections import Counter




LOW_STOCK_LIMIT = 10        # at or below this quantity -> LOW STOCK ALERT
EXPIRING_SOON_DAYS = 30     # expires within this many days ->"expiring soon"


class ValidationError(Exception):
    """Raised when user data breaks a business rule or validation rule."""


def require_text(value, field_name):
    value = str(value).strip()
    if not value:
        raise ValidationError(f"Error: {field_name} cannot be empty.")
    return value


def validate_id(value, field_name):
    value = require_text(value, field_name)
    if " " in value:
        raise ValidationError(f"Error: {field_name} must not contain spaces.")
    return value


def validate_phone(phone):
    phone = require_text(phone, "Phone number")
    allowed = set("0123456789+-() ")
    if any(character not in allowed for character in phone):
        raise ValidationError("Error: Phone number contains invalid characters.")

    digits = [character for character in phone if character.isdigit()]
    if len(digits) < 7:
        raise ValidationError("Error: Phone number must contain at least 7 digits.")
    return phone


def validate_email(email):
    email = require_text(email, "Email")
    if "@" not in email or "." not in email:
        raise ValidationError("Error: Invalid email address.")
    return email


def parse_date(value):
    if isinstance(value, date):
        return value

    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Error: Date must be valid and use YYYY-MM-DD format.")


def format_money(value):
    return f"${value:.2f}"


class Person:
    """Base class (parent) for anyone the pharmacy deals with.

    Stores the data every person shares (ID, name, phone) and the
    validation rules for it. Customer and Supplier inherit from this
    class and override display_info() (polymorphism).
    """

    def __init__(self, person_id, name, phone):
        self.__person_id = validate_id(person_id, "ID")
        self.__name = require_text(name, "Name")
        self.__phone = validate_phone(phone)

    @property
    def person_id(self):
        return self.__person_id

    @person_id.setter
    def person_id(self, value):
        self.__person_id = validate_id(value, "ID")

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = require_text(value, "Name")

    @property
    def phone(self):
        return self.__phone

    @phone.setter
    def phone(self, value):
        self.__phone = validate_phone(value)

    def display_info(self):
        return f"Person: {self.name} | Phone: {self.phone}"


class Customer(Person):
    """A pharmacy customer.

    Child class of Person: it reuses the parent constructor with
    super().__init__() and only adds nothing extra except its own
    overridden display_info().
    """

    def __init__(self, customer_id, name, phone):
        super().__init__(customer_id, name, phone)

    @property
    def customer_id(self):
        return self.person_id

    def display_info(self):
        return f"Customer [{self.customer_id}] {self.name} | Phone: {self.phone}"


class Supplier(Person):
    """A medicine supplier.

    Child class of Person: reuses ID/name/phone handling through
    super().__init__() and extends it with email and address.
    """

    def __init__(self, supplier_id, name, phone, email, address):
        super().__init__(supplier_id, name, phone)
        self.__email = validate_email(email)
        self.__address = require_text(address, "Address")

    @property
    def supplier_id(self):
        return self.person_id

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        self.__email = validate_email(value)

    @property
    def address(self):
        return self.__address

    @address.setter
    def address(self, value):
        self.__address = require_text(value, "Address")

    def display_info(self):
        return (
            f"Supplier [{self.supplier_id}] {self.name} | Phone: {self.phone} | "
            f"Email: {self.email} | Address: {self.address}"
        )


class Category:
    """A medicine category (e.g. Painkillers, Vitamins)."""

    def __init__(self, category_id, name, description):
        self.__category_id = validate_id(category_id, "Category ID")
        self.__name = require_text(name, "Category name")
        self.__description = require_text(description, "Category description")

    @property
    def category_id(self):
        return self.__category_id

    @category_id.setter
    def category_id(self, value):
        self.__category_id = validate_id(value, "Category ID")

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = require_text(value, "Category name")

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = require_text(value, "Category description")

    def display_info(self):
        return f"Category [{self.category_id}] {self.name} - {self.description}"


class Medicine:
    """A medicine stored in the pharmacy inventory.

    Encapsulation example: price and quantity are private attributes
    (self.__price, self.__quantity) and can only be changed through
    their property setters, which validate every new value. This is
    how the business rules (positive price, non-negative stock) are
    enforced no matter who tries to change the data.
    """

    def __init__(
        self,
        medicine_id,
        name,
        category,
        price,
        quantity,
        expiration_date,
        supplier,
        active=True,
    ):
        self.__medicine_id = validate_id(medicine_id, "Medicine ID")
        self.__name = require_text(name, "Medicine name")
        self.category = category
        self.__price = 0
        self.__quantity = 0
        self.price = price
        self.quantity = quantity
        self.expiration_date = parse_date(expiration_date)
        self.supplier = supplier
        self.active = bool(active)

    @property
    def medicine_id(self):
        return self.__medicine_id

    @medicine_id.setter
    def medicine_id(self, value):
        self.__medicine_id = validate_id(value, "Medicine ID")

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = require_text(value, "Medicine name")

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, value):
        """Set the price. Business Rule 3: price must be positive."""
        try:
            value = float(value)
        except ValueError:
            raise ValidationError("Error: Invalid price.")

        if value <= 0:
            raise ValidationError("Error: Medicine price must be positive.")
        self.__price = value

    @property
    def quantity(self):
        return self.__quantity

    @quantity.setter
    def quantity(self, value):
        """Set the stock quantity. Business rule: never negative."""
        try:
            value = int(value)
        except ValueError:
            raise ValidationError("Error: Invalid quantity.")

        if value < 0:
            raise ValidationError("Error: Quantity cannot be negative.")
        self.__quantity = value

    def is_expired(self, reference_date=None):
        reference_date = reference_date or date.today()
        return self.expiration_date < reference_date

    def expires_soon(self, days=EXPIRING_SOON_DAYS, reference_date=None):
        reference_date = reference_date or date.today()
        soon_limit = reference_date + timedelta(days=days)
        return reference_date <= self.expiration_date <= soon_limit

    def is_low_stock(self, limit=LOW_STOCK_LIMIT):
        return self.quantity <= limit

    def reduce_stock(self, quantity):
        """Deduct sold quantity from stock.

        Business Rule 2: the sale quantity can never exceed the
        available stock, so the stock can never become negative.
        """
        if quantity <= 0:
            raise ValidationError("Error: Sale quantity must be greater than zero.")
        if quantity > self.quantity:
            raise ValidationError("Error: Insufficient stock.")
        self.quantity -= quantity

    def display_info(self):
        status = "Active" if self.active else "Inactive"
        expired = "Expired" if self.is_expired() else "Not expired"
        return (
            f"Medicine [{self.medicine_id}] {self.name} | "
            f"Category: {self.category.name} | Price: {format_money(self.price)} | "
            f"Stock: {self.quantity} | Expires: {self.expiration_date} | "
            f"Supplier: {self.supplier.name} | {status} | {expired}"
        )


class SaleItem:
    """One line inside a sale: a medicine, a quantity and its subtotal.

    subtotal = quantity x unit_price
    """

    def __init__(self, medicine, quantity, unit_price=None):
        if quantity <= 0:
            raise ValidationError("Error: Sale quantity must be greater than zero.")

        self.medicine = medicine
        self.quantity = int(quantity)
        self.unit_price = float(unit_price if unit_price is not None else medicine.price)
        self.subtotal = self.quantity * self.unit_price

    def display_info(self):
        return (
            f"{self.medicine.name} x {self.quantity} @ "
            f"{format_money(self.unit_price)} = {format_money(self.subtotal)}"
        )


class Sale:
    """A complete sale: one customer, one date, one or more SaleItems.

    total price = sum of all item subtotals
    """

    def __init__(self, sale_id, customer, sale_items, sale_date=None):
        self.sale_id = validate_id(sale_id, "Sale ID")
        self.customer = customer
        self.date = parse_date(sale_date) if sale_date else date.today()
        self.sale_items = sale_items
        self.total_price = sum(item.subtotal for item in sale_items)

    def total_items(self):
        return sum(item.quantity for item in self.sale_items)

    def display_info(self):
        lines = [
            f"Sale [{self.sale_id}]",
            f"Customer: {self.customer.name}",
            f"Date: {self.date}",
            "Items:",
        ]
        for item in self.sale_items:
            lines.append(f"  - {item.display_info()}")
        lines.append(f"Total: {format_money(self.total_price)}")
        return "\n".join(lines)


class Pharmacy:
    """Main manager class of the whole system.

    It stores every collection (medicines, categories, suppliers,
    customers, sales) and provides all application operations:
    CRUD, search, filters, sales, low-stock alerts, expiration
    tracking and the sales report.
    """

    def __init__(self, name="City Pharmacy"):
        self.name = require_text(name, "Pharmacy name")
        self.medicines = {}
        self.categories = {}
        self.suppliers = {}
        self.customers = {}
        self.sales = {}

    def _ensure_unique_id(self, collection, item_id, item_name):
        if item_id in collection:
            raise ValidationError(f"Error: {item_name} ID already exists.")

    def _get_or_error(self, collection, item_id, item_name):
        item_id = validate_id(item_id, f"{item_name} ID")
        if item_id not in collection:
            raise ValidationError(f"{item_name} not found.")
        return collection[item_id]

    # Category CRUD
    def add_category(self, category):
        self._ensure_unique_id(self.categories, category.category_id, "Category")
        self.categories[category.category_id] = category
        return f"Category added: {category.name}"

    def view_categories(self):
        return list(self.categories.values())

    def update_category(self, category_id, name=None, description=None):
        category = self._get_or_error(self.categories, category_id, "Category")
        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
        return f"Category updated: {category.name}"

    def delete_category(self, category_id):
        category = self._get_or_error(self.categories, category_id, "Category")
        del self.categories[category.category_id]
        return f"Category deleted: {category.name}"

    # Supplier CRUD
    def add_supplier(self, supplier):
        self._ensure_unique_id(self.suppliers, supplier.supplier_id, "Supplier")
        self.suppliers[supplier.supplier_id] = supplier
        return f"Supplier added: {supplier.name}"

    def view_suppliers(self):
        return list(self.suppliers.values())

    def update_supplier(self, supplier_id, name=None, phone=None, email=None, address=None):
        supplier = self._get_or_error(self.suppliers, supplier_id, "Supplier")
        if name is not None:
            supplier.name = name
        if phone is not None:
            supplier.phone = phone
        if email is not None:
            supplier.email = email
        if address is not None:
            supplier.address = address
        return f"Supplier updated: {supplier.name}"

    def delete_supplier(self, supplier_id):
        supplier = self._get_or_error(self.suppliers, supplier_id, "Supplier")
        del self.suppliers[supplier.supplier_id]
        return f"Supplier deleted: {supplier.name}"

    # Customer CRUD
    def add_customer(self, customer):
        self._ensure_unique_id(self.customers, customer.customer_id, "Customer")
        self.customers[customer.customer_id] = customer
        return f"Customer added: {customer.name}"

    def view_customers(self):
        return list(self.customers.values())

    def update_customer(self, customer_id, name=None, phone=None):
        customer = self._get_or_error(self.customers, customer_id, "Customer")
        if name is not None:
            customer.name = name
        if phone is not None:
            customer.phone = phone
        return f"Customer updated: {customer.name}"

    def delete_customer(self, customer_id):
        customer = self._get_or_error(self.customers, customer_id, "Customer")
        del self.customers[customer.customer_id]
        return f"Customer deleted: {customer.name}"

    # Medicine CRUD
    def add_medicine(self, medicine):
        self._ensure_unique_id(self.medicines, medicine.medicine_id, "Medicine")
        self.medicines[medicine.medicine_id] = medicine
        return f"Medicine added: {medicine.name}"

    def view_medicines(self):
        return list(self.medicines.values())

    def update_medicine(
        self,
        medicine_id,
        name=None,
        category=None,
        price=None,
        quantity=None,
        expiration_date=None,
        supplier=None,
        active=None,
    ):
        medicine = self._get_or_error(self.medicines, medicine_id, "Medicine")
        if name is not None:
            medicine.name = name
        if category is not None:
            medicine.category = category
        if price is not None:
            medicine.price = price
        if quantity is not None:
            medicine.quantity = quantity
        if expiration_date is not None:
            medicine.expiration_date = parse_date(expiration_date)
        if supplier is not None:
            medicine.supplier = supplier
        if active is not None:
            medicine.active = bool(active)
        return f"Medicine updated: {medicine.name}"

    def delete_medicine(self, medicine_id):
        medicine = self._get_or_error(self.medicines, medicine_id, "Medicine")
        del self.medicines[medicine.medicine_id]
        return f"Medicine deleted: {medicine.name}"

    # Search and filters
    def search_medicine(self, medicine_id=None, name=None, category=None):
        """Search medicines by ID (exact), name (partial) or category.

        All comparisons are case-insensitive; matching is partial for
        names and categories so "pan" finds "Panadol".
        """
        results = list(self.medicines.values())

        if medicine_id:
            results = [
                medicine
                for medicine in results
                if medicine.medicine_id.lower() == medicine_id.lower()
            ]
        if name:
            name = name.lower()
            results = [medicine for medicine in results if name in medicine.name.lower()]
        if category:
            category = category.lower()
            results = [
                medicine
                for medicine in results
                if category in medicine.category.name.lower()
                or category == medicine.category.category_id.lower()
            ]
        return results

    def filter_available_medicines(self):
        return [medicine for medicine in self.medicines.values() if medicine.quantity > 0]

    def filter_out_of_stock_medicines(self):
        return [medicine for medicine in self.medicines.values() if medicine.quantity == 0]

    def filter_low_stock_medicines(self, limit=LOW_STOCK_LIMIT):
        return [medicine for medicine in self.medicines.values() if medicine.is_low_stock(limit)]

    def filter_expired_medicines(self):
        return [medicine for medicine in self.medicines.values() if medicine.is_expired()]

    def filter_expiring_soon_medicines(self, days=EXPIRING_SOON_DAYS):
        return [medicine for medicine in self.medicines.values() if medicine.expires_soon(days)]

    def filter_active_medicines(self):
        return [medicine for medicine in self.medicines.values() if medicine.active]

    def filter_inactive_medicines(self):
        return [medicine for medicine in self.medicines.values() if not medicine.active]

    def filter_below_stock(self, threshold):
        """Return medicines whose stock is below the given number.

        Example: filter_below_stock(10) answers
        "Show medicines with stock less than 10".
        """
        try:
            threshold = int(threshold)
        except (TypeError, ValueError):
            raise ValidationError("Error: Invalid quantity.")
        return [
            medicine
            for medicine in self.medicines.values()
            if medicine.quantity < threshold
        ]

    # Required display helpers
    def show_inventory(self):
        return self.view_medicines()

    def show_low_stock(self, limit=LOW_STOCK_LIMIT):
        return self.filter_low_stock_medicines(limit)

    def show_expired_medicines(self):
        return self.filter_expired_medicines()

    def show_expiring_soon(self, days=EXPIRING_SOON_DAYS):
        return self.filter_expiring_soon_medicines(days)

    # Sales
    def create_sale(self, sale_id, customer_id, item_requests, sale_date=None):
        """Record a sale and update the inventory automatically.

        item_requests is a list of (medicine_id, quantity) pairs.
        Validation runs in two passes so a sale is never half
        applied: first every requested item is checked (medicine
        exists, active, not expired, enough stock), and only when
        ALL items pass is the stock deducted and the Sale created.
        """
        self._ensure_unique_id(self.sales, sale_id, "Sale")
        customer = self._get_or_error(self.customers, customer_id, "Customer")

        if not item_requests:
            raise ValidationError("Error: Sale must contain at least one item.")

        checked_items = []
        # Pass 1: validate every requested item (nothing is deducted yet).
        for medicine_id, quantity in item_requests:
            medicine = self._get_or_error(self.medicines, medicine_id, "Medicine")
            try:
                quantity = int(quantity)
            except ValueError:
                raise ValidationError("Error: Invalid quantity.")

            if quantity <= 0:
                raise ValidationError("Error: Sale quantity must be greater than zero.")
            if not medicine.active:
                raise ValidationError("Error: Inactive medicine cannot be sold.")
            if medicine.is_expired():
                raise ValidationError("Error: This medicine has expired and cannot be sold.")
            if quantity > medicine.quantity:
                raise ValidationError("Error: Insufficient stock.")

            checked_items.append((medicine, quantity))

        sale_items = []
        # Pass 2: all items are valid -> deduct stock and build the sale.
        for medicine, quantity in checked_items:
            medicine.reduce_stock(quantity)
            sale_items.append(SaleItem(medicine, quantity))

        sale = Sale(sale_id, customer, sale_items, sale_date)
        self.sales[sale.sale_id] = sale
        return sale

    def generate_sales_report(self):
        """Build the full sales report (counts, revenue, most sold)."""
        number_of_sales = len(self.sales)
        total_revenue = sum(sale.total_price for sale in self.sales.values())
        total_items_sold = sum(sale.total_items() for sale in self.sales.values())

        sold_counter = Counter()
        for sale in self.sales.values():
            for item in sale.sale_items:
                sold_counter[item.medicine.name] += item.quantity

        most_sold = None
        if sold_counter:
            most_sold = sold_counter.most_common(1)[0]

        lines = [
            "========== SALES REPORT ==========",
            f"Number of Sales: {number_of_sales}",
            f"Total Items Sold: {total_items_sold}",
            f"Total Revenue: {format_money(total_revenue)}",
        ]

        if most_sold:
            lines.append(f"Most Sold Medicine: {most_sold[0]} ({most_sold[1]} units)")
        else:
            lines.append("Most Sold Medicine: None")

        lines.append("")
        lines.append("Sales Details:")
        if not self.sales:
            lines.append("No sales recorded.")
        else:
            for sale in self.sales.values():
                lines.append("-" * 34)
                lines.append(sale.display_info())

        lines.append("=" * 34)
        return "\n".join(lines)


class ConsoleMenu:
    """Interactive console menu (the user interface of the system).

    The menu only reads input and prints output - all real work is
    delegated to the Pharmacy class, which keeps the UI and the
    business logic cleanly separated.
    """

    def __init__(self, pharmacy):
        self.pharmacy = pharmacy

    def run(self):
        """Show the main menu repeatedly until the user chooses Exit."""
        while True:
            print("\n====================================")
            print("       PHARMACY MANAGEMENT SYSTEM")
            print("====================================")
            print("1. Manage Medicines")
            print("2. Manage Categories")
            print("3. Manage Suppliers")
            print("4. Manage Customers")
            print("5. Record Sale")
            print("6. Search Medicine")
            print("7. View Inventory")
            print("8. Low Stock Alerts")
            print("9. Expiration Tracking")
            print("10. Sales Report")
            print("0. Exit")

            try:
                choice = input("Enter your choice: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            try:
                if choice == "1":
                    self.manage_medicines()
                elif choice == "2":
                    self.manage_categories()
                elif choice == "3":
                    self.manage_suppliers()
                elif choice == "4":
                    self.manage_customers()
                elif choice == "5":
                    self.record_sale()
                elif choice == "6":
                    self.search_medicine()
                elif choice == "7":
                    self.view_inventory_menu()
                elif choice == "8":
                    self.print_low_stock()
                elif choice == "9":
                    self.expiration_tracking()
                elif choice == "10":
                    print(self.pharmacy.generate_sales_report())
                elif choice == "0":
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice.")
            except ValidationError as error:
                print(error)
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            except Exception as error:
                print(f"Unexpected error: {error}")

    def print_collection(self, collection, title):
        print(f"\n========== {title} ==========")
        if not collection:
            print("No records found.")
            return
        for item in collection:
            print(item.display_info())

    def view_inventory_menu(self):
        """Submenu for option 7: view the inventory or apply a filter."""
        print("\n--- View Inventory / Filters ---")
        print("1. View all medicines")
        print("2. Available medicines (in stock)")
        print("3. Out-of-stock medicines")
        print("4. Low-stock medicines (quantity <= 10)")
        print("5. Medicines with stock below a custom number")
        print("6. Active medicines")
        print("7. Inactive medicines")
        print("0. Back")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            self.print_collection(self.pharmacy.show_inventory(), "Inventory")
        elif choice == "2":
            self.print_collection(
                self.pharmacy.filter_available_medicines(), "Available Medicines"
            )
        elif choice == "3":
            self.print_collection(
                self.pharmacy.filter_out_of_stock_medicines(), "Out-of-Stock Medicines"
            )
        elif choice == "4":
            self.print_collection(
                self.pharmacy.filter_low_stock_medicines(), "Low-Stock Medicines"
            )
        elif choice == "5":
            threshold = input("Show medicines with stock less than: ").strip()
            self.print_collection(
                self.pharmacy.filter_below_stock(threshold),
                f"Medicines With Stock Below {threshold}",
            )
        elif choice == "6":
            self.print_collection(
                self.pharmacy.filter_active_medicines(), "Active Medicines"
            )
        elif choice == "7":
            self.print_collection(
                self.pharmacy.filter_inactive_medicines(), "Inactive Medicines"
            )
        elif choice == "0":
            return
        else:
            print("Invalid choice.")

    def choose_category(self):
        category_id = input("Enter category ID: ")
        return self.pharmacy._get_or_error(self.pharmacy.categories, category_id, "Category")

    def choose_supplier(self):
        supplier_id = input("Enter supplier ID: ")
        return self.pharmacy._get_or_error(self.pharmacy.suppliers, supplier_id, "Supplier")

    def manage_medicines(self):
        print("\n1. Add medicine")
        print("2. View medicines")
        print("3. Update medicine")
        print("4. Delete medicine")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            category = self.choose_category()
            supplier = self.choose_supplier()
            medicine = Medicine(
                input("Medicine ID: "),
                input("Name: "),
                category,
                input("Price: "),
                input("Quantity: "),
                input("Expiration date (YYYY-MM-DD): "),
                supplier,
                True,
            )
            print(self.pharmacy.add_medicine(medicine))
        elif choice == "2":
            self.print_collection(self.pharmacy.view_medicines(), "Medicines")
        elif choice == "3":
            medicine_id = input("Medicine ID to update: ")
            name = input("New name (leave empty to skip): ").strip() or None
            price = input("New price (leave empty to skip): ").strip() or None
            quantity = input("New quantity (leave empty to skip): ").strip() or None
            expiration_date = input("New expiration date (leave empty to skip): ").strip() or None
            active_text = input("Active? yes/no (leave empty to skip): ").strip().lower()
            active = None
            if active_text in ("yes", "y"):
                active = True
            elif active_text in ("no", "n"):
                active = False
            print(
                self.pharmacy.update_medicine(
                    medicine_id,
                    name=name,
                    price=price,
                    quantity=quantity,
                    expiration_date=expiration_date,
                    active=active,
                )
            )
        elif choice == "4":
            print(self.pharmacy.delete_medicine(input("Medicine ID to delete: ")))
        else:
            print("Invalid choice.")

    def manage_categories(self):
        print("\n1. Add category")
        print("2. View categories")
        print("3. Update category")
        print("4. Delete category")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            category = Category(
                input("Category ID: "),
                input("Name: "),
                input("Description: "),
            )
            print(self.pharmacy.add_category(category))
        elif choice == "2":
            self.print_collection(self.pharmacy.view_categories(), "Categories")
        elif choice == "3":
            category_id = input("Category ID to update: ")
            name = input("New name (leave empty to skip): ").strip() or None
            description = input("New description (leave empty to skip): ").strip() or None
            print(self.pharmacy.update_category(category_id, name, description))
        elif choice == "4":
            print(self.pharmacy.delete_category(input("Category ID to delete: ")))
        else:
            print("Invalid choice.")

    def manage_suppliers(self):
        print("\n1. Add supplier")
        print("2. View suppliers")
        print("3. Update supplier")
        print("4. Delete supplier")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            supplier = Supplier(
                input("Supplier ID: "),
                input("Name: "),
                input("Phone: "),
                input("Email: "),
                input("Address: "),
            )
            print(self.pharmacy.add_supplier(supplier))
        elif choice == "2":
            self.print_collection(self.pharmacy.view_suppliers(), "Suppliers")
        elif choice == "3":
            supplier_id = input("Supplier ID to update: ")
            name = input("New name (leave empty to skip): ").strip() or None
            phone = input("New phone (leave empty to skip): ").strip() or None
            email = input("New email (leave empty to skip): ").strip() or None
            address = input("New address (leave empty to skip): ").strip() or None
            print(self.pharmacy.update_supplier(supplier_id, name, phone, email, address))
        elif choice == "4":
            print(self.pharmacy.delete_supplier(input("Supplier ID to delete: ")))
        else:
            print("Invalid choice.")

    def manage_customers(self):
        print("\n1. Add customer")
        print("2. View customers")
        print("3. Update customer")
        print("4. Delete customer")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            customer = Customer(input("Customer ID: "), input("Name: "), input("Phone: "))
            print(self.pharmacy.add_customer(customer))
        elif choice == "2":
            self.print_collection(self.pharmacy.view_customers(), "Customers")
        elif choice == "3":
            customer_id = input("Customer ID to update: ")
            name = input("New name (leave empty to skip): ").strip() or None
            phone = input("New phone (leave empty to skip): ").strip() or None
            print(self.pharmacy.update_customer(customer_id, name, phone))
        elif choice == "4":
            print(self.pharmacy.delete_customer(input("Customer ID to delete: ")))
        else:
            print("Invalid choice.")

    def record_sale(self):
        sale_id = input("Sale ID: ")
        customer_id = input("Customer ID: ")
        item_requests = []

        while True:
            medicine_id = input("Medicine ID: ")
            quantity = input("Quantity: ")
            item_requests.append((medicine_id, quantity))

            another = input("Add another item? yes/no: ").strip().lower()
            if another not in ("yes", "y"):
                break

        sale = self.pharmacy.create_sale(sale_id, customer_id, item_requests)
        print("\nSale recorded successfully.")
        print(sale.display_info())

    def search_medicine(self):
        print("\nSearch by:")
        print("1. Medicine ID")
        print("2. Medicine name")
        print("3. Category")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            results = self.pharmacy.search_medicine(medicine_id=input("Enter medicine ID: "))
        elif choice == "2":
            results = self.pharmacy.search_medicine(name=input("Enter medicine name: "))
        elif choice == "3":
            results = self.pharmacy.search_medicine(category=input("Enter category: "))
        else:
            print("Invalid choice.")
            return

        self.print_collection(results, "Search Results")

    def print_low_stock(self):
        low_stock = self.pharmacy.show_low_stock()
        print("\n========== LOW STOCK ALERTS ==========")
        if not low_stock:
            print("No low-stock medicines.")
            return
        for medicine in low_stock:
            print("LOW STOCK ALERT")
            print(f"{medicine.name} - Only {medicine.quantity} units remaining")

    def expiration_tracking(self):
        expired = self.pharmacy.show_expired_medicines()
        expiring_soon = self.pharmacy.show_expiring_soon()

        print("\nExpired Medicines:")
        if not expired:
            print("No expired medicines.")
        for medicine in expired:
            print(f"- {medicine.name} - Expired: {medicine.expiration_date}")

        print("\nExpiring Soon:")
        if not expiring_soon:
            print("No medicines expiring soon.")
        for medicine in expiring_soon:
            print(f"- {medicine.name} - Expires: {medicine.expiration_date}")


def create_sample_pharmacy():
    """Build a pharmacy pre-filled with sample data for the demo."""
    pharmacy = Pharmacy("OOP Final Pharmacy")

    painkillers = Category("C001", "Painkillers", "Medicines used to reduce pain")
    vitamins = Category("C002", "Vitamins", "Supplements for daily health")
    antibiotics = Category("C003", "Antibiotics", "Medicines used for bacterial infections")

    main_supplier = Supplier(
        "S001",
        "MediSupply",
        "+201001234567",
        "orders@medisupply.com",
        "Cairo Medical Street",
    )
    second_supplier = Supplier(
        "S002",
        "HealthSource",
        "+201001112223",
        "sales@healthsource.com",
        "Alexandria Road",
    )

    customer = Customer("CU001", "Mostafa Nouh", "+201009998887")

    pharmacy.add_category(painkillers)
    pharmacy.add_category(vitamins)
    pharmacy.add_category(antibiotics)
    pharmacy.add_supplier(main_supplier)
    pharmacy.add_supplier(second_supplier)
    pharmacy.add_customer(customer)

    today = date.today()
    pharmacy.add_medicine(
        Medicine(
            "M001",
            "Panadol",
            painkillers,
            25.0,
            50,
            today + timedelta(days=365),
            main_supplier,
        )
    )
    pharmacy.add_medicine(
        Medicine(
            "M002",
            "Vitamin C",
            vitamins,
            40.0,
            7,
            today + timedelta(days=20),
            second_supplier,
        )
    )
    pharmacy.add_medicine(
        Medicine(
            "M003",
            "Old Cough Syrup",
            painkillers,
            30.0,
            15,
            today - timedelta(days=10),
            main_supplier,
        )
    )
    pharmacy.add_medicine(
        Medicine(
            "M004",
            "Amoxicillin",
            antibiotics,
            55.0,
            0,
            today + timedelta(days=180),
            second_supplier,
            active=False,
        )
    )

    return pharmacy


def run_demonstration(pharmacy):
    """Run the automatic demonstration required for the project.

    It shows, in order: adding medicines, searching, updating,
    recording a sale, automatic inventory updates, low-stock
    detection, expiration detection, the expired-medicine rule,
    the insufficient-stock rule, polymorphism and the sales report.
    """
    print("\n========== PHARMACY MANAGEMENT SYSTEM DEMO ==========")

    print("\n1. Adding medicines")
    for medicine in pharmacy.view_medicines():
        print(medicine.display_info())

    print("\n2. Searching for medicine name: Panadol")
    for medicine in pharmacy.search_medicine(name="Panadol"):
        print(medicine.display_info())

    print("\n3. Updating a medicine")
    print(pharmacy.update_medicine("M001", price=27.5, quantity=50))
    print(pharmacy.medicines["M001"].display_info())

    print("\n4. Recording a sale and updating inventory")
    print(f"Before Sale: Panadol Stock = {pharmacy.medicines['M001'].quantity}")
    sale = pharmacy.create_sale("SALE001", "CU001", [("M001", 5), ("M002", 2)])
    print(sale.display_info())
    print(f"After Sale: Panadol Stock = {pharmacy.medicines['M001'].quantity}")

    print("\n5. Low-stock detection")
    low_stock = pharmacy.show_low_stock()
    for medicine in low_stock:
        print("LOW STOCK ALERT")
        print(f"{medicine.name} - Only {medicine.quantity} units remaining")

    print("\n6. Expiration detection")
    print("Expired Medicines:")
    for medicine in pharmacy.show_expired_medicines():
        print(f"- {medicine.name} - Expired: {medicine.expiration_date}")

    print("\nExpiring Soon:")
    for medicine in pharmacy.show_expiring_soon():
        print(f"- {medicine.name} - Expires: {medicine.expiration_date}")

    print("\n7. Preventing sale of expired medicine")
    try:
        pharmacy.create_sale("SALE002", "CU001", [("M003", 1)])
    except ValidationError as error:
        print(error)

    print("\n8. Preventing sale when quantity exceeds stock")
    try:
        pharmacy.create_sale("SALE003", "CU001", [("M002", 999)])
    except ValidationError as error:
        print(error)

    print("\n9. Demonstrating polymorphism with Person references")
    people = [pharmacy.customers["CU001"], pharmacy.suppliers["S001"]]
    for person in people:
        print(person.display_info())

    print("\n10. Generating sales report")
    print(pharmacy.generate_sales_report())


if __name__ == "__main__":
    sample_pharmacy = create_sample_pharmacy()
    run_demonstration(sample_pharmacy)

    try:
        answer = input("\nOpen interactive console menu? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = "n"
    if answer in ("y", "yes"):
        ConsoleMenu(sample_pharmacy).run()
    else:
        print("Program finished.")
