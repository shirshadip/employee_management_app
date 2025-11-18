import tkinter as tk 
from tkinter import ttk , messagebox
import mysql.connector as m 
class EmployeeManagementSystem:
    def __init__(s,root) -> None:
        s.root=root
        s.root.title("employee management app")
        s.root.geometry("800x600")
        s.root.configure(bg="FFFFFF")
        #database connection
        s.db_config = {
            'host':'localhost',
            'user':'root',
            'password':'',
            'database':'emp'
        }
        s.conn=None
        s.cursor = None
        s.connect_db ()
        #styling 
        s.style = ttk.Style()
        s.style.theme_use("clam")#use clean theme for modern look 
        s.style.configure("TFrame",background="#f0f0f0")
        s.style.configure("TLable",background="#f0f0f0",font=("Inter",10))
        s.style.configure("TButton",font=("Inter",10,"bold"),padding=6,background="red",foreground="white",borderwidth=0,relief="flat")#flat button
        s.style.map("TButton",background = [('active',"#32CD32")],foreground =[('active','white' )])
        s.style.configure("Treeview:Heading",font=("Inter",10,"Bold"))
        s.style.configure("Treeview",font=("Inter",10),rowheight= 25)
        s.style.map('Treeview',background=[('selected','#a8dfff')])
        
        #.........main frame..........
        
        s.main_frame = ttk.Frame(root,padding="20")
        s.main_frame.pack(fill=tk.BOTH,expand=True)
                
        #title label 
        
        
        
        
    def connect_db(self):
        ttk.Label(self.main_frame,text="Employee management dashboard",font = ("Inter",18,"bold"),
                  background="#f0f0f0",foreground="#333").pack(pady=10)
        
        