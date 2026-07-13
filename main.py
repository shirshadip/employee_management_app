import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

import mysql.connector


class EmployeeManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Management System")
        self.root.geometry("900x650")
        self.root.minsize(760, 520)
        self.root.attributes('-fullscreen', False)
        self.root.resizable(True, True)

        # ---- Theme colors (single source of truth, no mismatched frames) ----
        self.COLOR_BG = "#f4f5f7"
        self.COLOR_CARD = "#ffffff"
        self.COLOR_ACCENT = "#e16c23"
        self.COLOR_ACCENT_HOVER = "#c95a17"
        self.COLOR_DANGER = "#c0392b"
        self.COLOR_DANGER_HOVER = "#a5301f"
        self.COLOR_TEXT = "#2b2b2b"
        self.COLOR_MUTED = "#6b6b6b"
        self.COLOR_BORDER = "#dcdde1"

        self.root.configure(bg=self.COLOR_BG)

        # ---- DB config: pull from environment, never hardcode credentials ----
        # Set these before running, e.g.:
        #   export DB_HOST=localhost DB_USER=root DB_PASSWORD=yourpassword DB_NAME=shirshadip_database
        self.db_config = {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'user': os.environ.get('DB_USER', 'root'),
            'passwd': os.environ.get('DB_PASSWORD', ''),
            'database': os.environ.get('DB_NAME', 'Employees'),
        }

        self.conn = None
        self.cursor = None
        self.all_rows = []  # cache for client-side search/filter

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._configure_styles()

        self._build_ui()

        # Try to connect after the UI exists, so a failure doesn't tear down
        # a half-built window (this was the root cause of the startup crash).
        self.connect_db(show_error=True)
        self.fetch_employees()

    # ------------------------------------------------------------------ #
    # Styling
    # ------------------------------------------------------------------ #
    def _configure_styles(self):
        s = self.style
        s.configure("TFrame", background=self.COLOR_BG)
        s.configure("Card.TFrame", background=self.COLOR_CARD)

        s.configure("TLabel", background=self.COLOR_BG, foreground=self.COLOR_TEXT, font=("Segoe UI", 10))
        s.configure("Card.TLabel", background=self.COLOR_CARD, foreground=self.COLOR_TEXT, font=("Segoe UI", 10))
        s.configure("Title.TLabel", background=self.COLOR_BG, foreground=self.COLOR_TEXT,
                    font=("Segoe UI", 18, "bold"))
        s.configure("Status.TLabel", background=self.COLOR_BG, font=("Segoe UI", 9))
        s.configure("Summary.TLabel", background=self.COLOR_BG, foreground=self.COLOR_MUTED,
                    font=("Segoe UI", 10, "bold"))

        s.configure("TEntry", padding=6)

        s.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=8,
                    background=self.COLOR_ACCENT, foreground="white", borderwidth=0)
        s.map("Accent.TButton", background=[('active', self.COLOR_ACCENT_HOVER)])

        s.configure("Danger.TButton", font=("Segoe UI", 10, "bold"), padding=8,
                    background=self.COLOR_DANGER, foreground="white", borderwidth=0)
        s.map("Danger.TButton", background=[('active', self.COLOR_DANGER_HOVER)])

        s.configure("Secondary.TButton", font=("Segoe UI", 10), padding=8,
                    background="#e2e3e6", foreground=self.COLOR_TEXT, borderwidth=0)
        s.map("Secondary.TButton", background=[('active', '#cfd0d3')])

        s.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#eceef1",
                    foreground=self.COLOR_TEXT)
        s.configure("Treeview", rowheight=26, font=("Segoe UI", 10),
                    background=self.COLOR_CARD, fieldbackground=self.COLOR_CARD)
        s.map("Treeview", background=[("selected", "#bcdcff")], foreground=[("selected", "#000000")])

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=20, style="TFrame")
        outer.pack(expand=True, fill=tk.BOTH)

        # Header row: title + connection status
        header = ttk.Frame(outer, style="TFrame")
        header.pack(fill=tk.X)
        ttk.Label(header, text="Employee Management Dashboard", style="Title.TLabel").pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Connecting...")
        self.status_label = ttk.Label(header, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack(side=tk.RIGHT, padx=(0, 4))

        # Input card
        input_card = ttk.Frame(outer, padding=16, style="Card.TFrame")
        input_card.pack(pady=(16, 10), fill=tk.X)

        labels = ["Name", "Position", "Salary"]
        self.entries = {}
        for i, text in enumerate(labels):
            ttk.Label(input_card, text=f"{text}:", style="Card.TLabel").grid(
                row=i, column=0, padx=(0, 10), pady=6, sticky="w")
            entry = ttk.Entry(input_card, width=42, font=("Segoe UI", 10))
            entry.grid(row=i, column=1, padx=5, pady=6, sticky="ew")
            self.entries[text.lower()] = entry
        input_card.grid_columnconfigure(1, weight=1)

        # Inline validation hint
        self.hint_var = tk.StringVar(value="")
        ttk.Label(input_card, textvariable=self.hint_var, style="Card.TLabel",
                  foreground=self.COLOR_DANGER).grid(row=len(labels), column=0, columnspan=2,
                                                       sticky="w", pady=(4, 0))

        # Action buttons
        button_row = ttk.Frame(outer, style="TFrame")
        button_row.pack(fill=tk.X, pady=(4, 12))
        ttk.Button(button_row, text="Add Employee", style="Accent.TButton",
                   command=self.add_employee).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Update Selected", style="Secondary.TButton",
                   command=self.update_employee).pack(side="left", padx=8)
        ttk.Button(button_row, text="Delete Selected", style="Danger.TButton",
                   command=self.delete_employee).pack(side="left", padx=8)
        ttk.Button(button_row, text="Clear Fields", style="Secondary.TButton",
                   command=self.clear_fields).pack(side="left", padx=8)
        ttk.Button(button_row, text="Reconnect", style="Secondary.TButton",
                   command=self.reconnect_db).pack(side="right")

        # Search row
        search_row = ttk.Frame(outer, style="TFrame")
        search_row.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(search_row, text="Search:").pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.apply_search())
        search_entry = ttk.Entry(search_row, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", fill=tk.X, expand=True)
        ttk.Button(search_row, text="Refresh", style="Secondary.TButton",
                   command=self.fetch_employees).pack(side="left", padx=(8, 0))

        # Table card
        tree_card = ttk.Frame(outer, padding=10, style="Card.TFrame")
        tree_card.pack(fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(tree_card)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.employee_tree = ttk.Treeview(
            tree_card, columns=("ID", "Name", "Position", "Salary"),
            show="headings", yscrollcommand=tree_scroll.set)
        self.employee_tree.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.employee_tree.yview)

        for col, w, anchor in [("ID", 60, "center"), ("Name", 220, "w"),
                                ("Position", 180, "w"), ("Salary", 140, "e")]:
            self.employee_tree.heading(col, text=col,
                                        command=lambda c=col: self.sort_by_column(c))
            self.employee_tree.column(col, width=w, anchor=anchor)

        self.employee_tree.tag_configure("oddrow", background="#f7f8fa")
        self.employee_tree.tag_configure("evenrow", background=self.COLOR_CARD)

        self.employee_tree.bind("<ButtonRelease-1>", self.select_employee)

        # Summary footer
        self.summary_var = tk.StringVar(value="")
        ttk.Label(outer, textvariable=self.summary_var, style="Summary.TLabel").pack(anchor="w", pady=(8, 0))

        self._sort_state = {"col": None, "reverse": False}

    # ------------------------------------------------------------------ #
    # Database
    # ------------------------------------------------------------------ #
    def connect_db(self, show_error=False):
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            self._set_status(True)
        except mysql.connector.Error as err:
            self.conn = None
            self.cursor = None
            self._set_status(False)
            if show_error:
                messagebox.showerror(
                    "Database Connection Error",
                    f"Could not connect to the database:\n\n{err}\n\n"
                    "You can keep the app open and click 'Reconnect' once the "
                    "database is reachable."
                )

    def reconnect_db(self):
        self.connect_db(show_error=True)
        if self.conn:
            self.fetch_employees()

    def _set_status(self, connected):
        if connected:
            self.status_var.set("● Connected")
            self.status_label.configure(foreground="#2e7d32")
        else:
            self.status_var.set("● Not connected")
            self.status_label.configure(foreground=self.COLOR_DANGER)

    def _db_ready(self):
        if not self.conn or not self.conn.is_connected():
            messagebox.showwarning(
                "Not Connected",
                "The app isn't connected to the database. Click 'Reconnect' and try again."
            )
            return False
        return True

    def fetch_employees(self):
        if not self._db_ready():
            return
        try:
            self.cursor.execute("SELECT id, name, position, salary FROM employees ORDER BY id DESC")
            self.all_rows = self.cursor.fetchall()
            self._render_rows(self.all_rows)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not fetch employees:\n\n{err}")

    def _render_rows(self, rows):
        self.employee_tree.delete(*self.employee_tree.get_children())
        total_salary = 0.0
        for i, row in enumerate(rows):
            emp_id, name, position, salary = row
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            display = (emp_id, name, position, f"${salary:,.2f}")
            self.employee_tree.insert("", tk.END, values=display, tags=(tag,))
            total_salary += float(salary)
        self.summary_var.set(f"{len(rows)} employee(s)  •  Total payroll: ${total_salary:,.2f}")

    def apply_search(self):
        term = self.search_var.get().strip().lower()
        if not term:
            self._render_rows(self.all_rows)
            return
        filtered = [r for r in self.all_rows
                    if term in str(r[1]).lower() or term in str(r[2]).lower()]
        self._render_rows(filtered)

    def sort_by_column(self, col):
        idx = {"ID": 0, "Name": 1, "Position": 2, "Salary": 3}[col]
        reverse = self._sort_state["col"] == col and not self._sort_state["reverse"]
        self._sort_state = {"col": col, "reverse": reverse}
        rows = sorted(self.all_rows, key=lambda r: r[idx], reverse=reverse)
        self._render_rows(rows)

    # ------------------------------------------------------------------ #
    # Form helpers
    # ------------------------------------------------------------------ #
    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.hint_var.set("")
        self.employee_tree.selection_remove(self.employee_tree.selection())

    def _read_form(self):
        """Validate and return (name, position, salary) or None if invalid."""
        name = self.entries['name'].get().strip()
        position = self.entries['position'].get().strip()
        salary_str = self.entries['salary'].get().strip()

        if not name or not position or not salary_str:
            self.hint_var.set("All fields are required.")
            return None
        try:
            salary = float(salary_str)
        except ValueError:
            self.hint_var.set("Salary must be a valid number.")
            return None
        if salary < 0:
            self.hint_var.set("Salary cannot be negative.")
            return None

        self.hint_var.set("")
        return name, position, salary

    # ------------------------------------------------------------------ #
    # CRUD actions
    # ------------------------------------------------------------------ #
    def add_employee(self):
        if not self._db_ready():
            return
        data = self._read_form()
        if data is None:
            return
        name, position, salary = data
        try:
            self.cursor.execute(
                "INSERT INTO employees (name, position, salary) VALUES (%s, %s, %s)",
                (name, position, salary))
            self.conn.commit()
            messagebox.showinfo("Success", f"Employee '{name}' added.")
            self.clear_fields()
            self.fetch_employees()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add employee:\n\n{err}")

    def update_employee(self):
        if not self._db_ready():
            return
        selected_item = self.employee_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Select an employee in the table first.")
            return
        employee_id = self.employee_tree.item(selected_item, 'values')[0]

        data = self._read_form()
        if data is None:
            return
        name, position, salary = data
        try:
            self.cursor.execute(
                "UPDATE employees SET name=%s, position=%s, salary=%s WHERE id=%s",
                (name, position, salary, employee_id))
            self.conn.commit()
            messagebox.showinfo("Success", f"Employee '{name}' updated.")
            self.clear_fields()
            self.fetch_employees()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to update employee:\n\n{err}")

    def delete_employee(self):
        if not self._db_ready():
            return
        selected_item = self.employee_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Select an employee to delete.")
            return
        values = self.employee_tree.item(selected_item, 'values')
        employee_id, name = values[0], values[1]

        confirm = messagebox.askyesno("Confirm Delete", f"Delete employee '{name}'? This cannot be undone.")
        if not confirm:
            return
        try:
            self.cursor.execute("DELETE FROM employees WHERE id=%s", (employee_id,))
            self.conn.commit()
            messagebox.showinfo("Success", f"Employee '{name}' deleted.")
            self.clear_fields()
            self.fetch_employees()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to delete employee:\n\n{err}")

    def select_employee(self, event):
        self.clear_fields()
        selected_item = self.employee_tree.focus()
        if selected_item:
            values = self.employee_tree.item(selected_item, 'values')
            self.entries['name'].insert(0, values[1])
            self.entries['position'].insert(0, values[2])
            # strip formatting ($ and commas) back to a plain number for editing
            raw_salary = str(values[3]).replace('$', '').replace(',', '')
            self.entries['salary'].insert(0, raw_salary)

    def on_closing(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn and self.conn.is_connected():
                self.conn.close()
        finally:
            self.root.destroy()


def _set_window_icon(root):
    """Load an optional window icon; safe no-op if none is bundled."""
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    png_path = os.path.join(base_dir, "app.png")
    ico_path = os.path.join(base_dir, "app.ico")
    try:
        if os.path.exists(png_path):
            root.iconphoto(False, tk.PhotoImage(file=png_path))
        elif os.path.exists(ico_path):
            root.iconbitmap(ico_path)
    except Exception as e:
        print("Warning: could not set window icon:", e)


if __name__ == "__main__":
    root = tk.Tk()
    _set_window_icon(root)
    app = EmployeeManagementSystem(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()