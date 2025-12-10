import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import os

class EmployeeManagementSystem:
    def __init__(self, root):
        self.root = root
        # Friendly application name and ensure windowed (not fullscreen)
        self.root.title("EmployeeManagementSystem")
        self.root.geometry("800x600")
        # Ensure the window is not started in fullscreen by mistake and is resizable
        try:
            self.root.attributes('-fullscreen', False)
        except Exception:
            pass
        self.root.resizable(True, True)
        self.root.configure(bg="#DDDDDB")

        # database conn
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'passwd': 'Shirshadip@123',
            'database': 'shirshadip_database'
        }
        #database is hosten on wamp server localhost
        self.conn = None
        self.cursor = None
        self.connect_db()

        # styling
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#fffff4", font=("Inter", 10))
        self.style.configure("TButton", font=("Inter", 10, "bold"), padding=6,
                             background="#e16c23", foreground="white", borderwidth=0, relief="flat")
        self.style.map("TButton", background=[('active', '#45a049')])
        self.style.configure("Treeview.Heading", font=("Inter", 10, "bold"))
        self.style.configure("Treeview", rowheight=25)
        self.style.map("Treeview", background=[("selected", "#a8dfff")])

        # main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(expand=True)

        # title label
        ttk.Label(self.main_frame, text="Employee Management Dashboard",
                  font=("Inter", 18, "bold"), background="#f0f0f0", foreground="#333").pack(pady=10)

        # input frame
        self.input_frame = ttk.Frame(self.main_frame, padding="15",
                                     relief="groove", borderwidth=2, style="TFrame")
        self.input_frame.pack(pady=10, fill=tk.X)

        labels = ["Name:", "position:", "salary:"]
        self.entries = {}

        for i, text in enumerate(labels):
            ttk.Label(self.input_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(self.input_frame, width=40, font=("Inter", 10))
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.entries[text.lower().replace(':', '')] = entry

        self.input_frame.grid_columnconfigure(1, weight=1)

        # button frame
        self.button_frame = ttk.Frame(self.main_frame, padding="10", style="TFrame")
        self.button_frame.pack(pady=10, fill=tk.X)

        ttk.Button(self.button_frame, text="Add Employee", command=self.add_employee).pack(side="left", padx=5, pady=5)
        ttk.Button(self.button_frame, text="Update Employee", command=self.update_employee).pack(side="left", padx=5, pady=5)
        ttk.Button(self.button_frame, text="Delete Employee", command=self.delete_employee).pack(side="left", padx=5, pady=5)
        ttk.Button(self.button_frame, text="Clear Fields", command=self.clear_fields).pack(side="left", padx=5, pady=5)

        for i in range(4):
            self.button_frame.grid_columnconfigure(i, weight=1)


        # emp list
        self.tree_frame = ttk.Frame(self.main_frame, padding="10", style="TFrame")
        self.tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # scrollbar
        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.employee_tree = ttk.Treeview(self.tree_frame, columns=("ID", "Name", "Position", "Salary"),
                                          show="headings", yscrollcommand=self.tree_scroll.set)
        self.employee_tree.pack(fill=tk.BOTH, expand=True)
        self.tree_scroll.config(command=self.employee_tree.yview)

        # define headings
        self.employee_tree.heading("ID", text="ID")
        self.employee_tree.heading("Name", text="Name")
        self.employee_tree.heading("Position", text="Position")
        self.employee_tree.heading("Salary", text="Salary")

        # define column widths
        self.employee_tree.column("ID", width=50, anchor="center")
        self.employee_tree.column("Name", width=200, anchor="w")
        self.employee_tree.column("Position", width=150, anchor="w")
        self.employee_tree.column("Salary", width=100, anchor="e")

        # Bind select event
        self.employee_tree.bind("<ButtonRelease-1>", self.select_employee)

        self.fetch_employees()


    def connect_db(self):
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error:
            messagebox.showerror("DB connector Error", "Cannot connect to database.")
            self.root.destroy()


    def fetch_employees(self):
        if not self.conn or not self.conn.is_connected():
            messagebox.showwarning("Database Not connected", "Cannot fetch employees, database is not connected")
            return

        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)

        try:
            sql = "SELECT id, name, position, salary FROM employees ORDER BY id DESC"
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            for row in rows:
                self.employee_tree.insert("", tk.END, values=row)
        except mysql.connector.Error:
            messagebox.showerror("Database Error", "Could not fetch employees")


    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)


    def add_employee(self):
        if not self.conn or not self.conn.is_connected():
            messagebox.showwarning("Database Not connected", "Cannot add employee. Database is not connected")
            return

        name = self.entries['name'].get().strip()
        position = self.entries['position'].get().strip()
        salary_str = self.entries['salary'].get().strip()

        if not name or not position or not salary_str:
            messagebox.showwarning("Input error", "All fields are required")
            return

        try:
            salary = float(salary_str)
            if salary < 0:
                messagebox.showwarning("Input error", "Salary cannot be negative")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Salary must be a valid number!")
            return

        try:
            sql = "INSERT INTO employees(name, position, salary) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, (name, position, salary))
            self.conn.commit()
            messagebox.showinfo("Success", "Employee added")
            self.clear_fields()
            self.fetch_employees()
        except mysql.connector.Error:
            messagebox.showerror("Database error", "Failed to add employee")


    def update_employee(self):
        if not self.conn or not self.conn.is_connected():
            messagebox.showwarning("Database not connected")
            return

        selected_item = self.employee_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection error", "Select an employee first")
            return

        employee_id = self.employee_tree.item(selected_item, 'values')[0]

        name = self.entries['name'].get().strip()
        position = self.entries['position'].get().strip()
        salary_str = self.entries['salary'].get().strip()

        if not name or not position or not salary_str:
            messagebox.showwarning("Input error", "All fields are required")
            return

        try:
            salary = float(salary_str)
            if salary < 0:
                messagebox.showwarning("Input error")
                return
        except ValueError:
            messagebox.showwarning("Input Error")
            return

        try:
            sql = "UPDATE employees SET name=%s, position=%s, salary=%s WHERE id=%s"
            self.cursor.execute(sql, (name, position, salary, employee_id))
            self.conn.commit()
            messagebox.showinfo("Success", "Employee updated successfully")
            self.clear_fields()
            self.fetch_employees()
        except mysql.connector.Error:
            messagebox.showerror("Database error", "Failed to update employee")


    def delete_employee(self):
        if not self.conn or not self.conn.is_connected():
            messagebox.showwarning("Database is not connected")
            return

        selected_item = self.employee_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection error", "Select an employee to delete")
            return

        employee_id = self.employee_tree.item(selected_item, 'values')[0]

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure?")
        if confirm:
            try:
                sql = "DELETE FROM employees WHERE id=%s"
                self.cursor.execute(sql, (employee_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Employee deleted")
                self.clear_fields()
                self.fetch_employees()
            except mysql.connector.Error:
                messagebox.showerror("Database Error", "Failed to delete employee")


    def select_employee(self, event):
        self.clear_fields()
        selected_item = self.employee_tree.focus()
        if selected_item:
            values = self.employee_tree.item(selected_item, 'values')
            self.entries['name'].insert(0, values[1])
            self.entries['position'].insert(0, values[2])
            self.entries['salary'].insert(0, values[3])


    def on_closing(self):
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    # Load window icon robustly: look in the script directory or the
    # PyInstaller extraction folder (sys._MEIPASS) for app.png or app.ico.
    try:
        import sys

        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        png_path = os.path.join(base_dir, "app.png")
        ico_path = os.path.join(base_dir, "app.ico")

        if os.path.exists(png_path):
            try:
                root.iconphoto(False, tk.PhotoImage(file=png_path))
            except Exception:
                # If PhotoImage fails for any reason, fall back to .ico
                if os.path.exists(ico_path):
                    try:
                        root.iconbitmap(ico_path)
                    except Exception:
                        pass
        elif os.path.exists(ico_path):
            try:
                root.iconbitmap(ico_path)
            except Exception:
                pass
        else:
            # No icon file bundled; continue without setting an icon
            pass
    except Exception as e:
        # Unexpected error while setting icon; continue execution.
        print("Warning: could not set window icon:", e)

    app = EmployeeManagementSystem(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
