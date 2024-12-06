from datetime import datetime
import re
import customtkinter as ctk
from tkinter import messagebox, ttk, simpledialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
import os

class Database:
    def __init__(self, db_name="real_estate.sqlite"):
        if not os.path.exists(db_name):
            self.connection = sqlite3.connect(db_name)
            self.cursor = self.connection.cursor()
            self.create_tables()
            self.create_superuser()
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

        

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Appartment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area REAL NOT NULL,
                rooms INTEGER NOT NULL,
                floor INTEGER NOT NULL,
                price REAL NOT NULL,
                sale_status INTEGER NOT NULL,
                estate_id INTEGER NOT NULL,
                FOREIGN KEY(estate_id) REFERENCES Estate(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Estate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                builder_id INTEGER,
                location TEXT NOT NULL,
                construction_date DATE,
                status INTEGER NOT NULL,
                comment TEXT,
                FOREIGN KEY (builder_id) REFERENCES Builder(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Auth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                builder_id INTEGER,
                FOREIGN KEY (builder_id) REFERENCES Builder(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Builders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                office_address TEXT,
                contact_number TEXT,
                foundation_date DATE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Bought_Appartments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Appartment_id INTEGER NOT NULL,
                owner_id INTEGER NOT NULL,
                purchase_date DATE NOT NULL,
                tax REAL,
                purchase_price REAL NOT NULL,
                FOREIGN KEY (Appartment_id) REFERENCES Appartment(id),
                FOREIGN KEY (owner_id) REFERENCES Auth(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                appartment_id DATE NOT NULL,
                FOREIGN KEY (appartment_id) REFERENCES Appartment(id),
                FOREIGN KEY (client_id) REFERENCES Auth(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                surname TEXT NOT NULL,
                name TEXT NOT NULL,
                patronymic TEXT NOT NULL,
                contact_number TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES Auth(id)
            )
        ''')

        self.connection.commit()
    def create_superuser(self):
        self.cursor.execute('''
            INSERT INTO Auth (login, password, role) VALUES ("admin", "password", "admin")
        ''')
        self.cursor.execute('''
            INSERT INTO Auth (login, password, role, builder_id) VALUES ("bd", "pwd", "builder", 1)
        ''')
        self.connection.commit()
    def fetch(self, query, args = None):
        if not args:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, args)
        rows = self.cursor.fetchall()
        return rows
    def fetch_one(self, query, args = None):
        if not args:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, args)
        row = self.cursor.fetchone()
        return row
    def execute(self, query, args = None):
        if not args:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, args)
        self.connection.commit()
    def __del__(self):
        self.connection.close()

class WelcomePage(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Welcome")
        self.geometry("600x400")

        # Название
        title_label = ctk.CTkLabel(self, text="Real Estate Management", font=("Calibri", 24))
        title_label.pack(pady=50)

        # Кнопка авторизации
        auth_button = ctk.CTkButton(self, text="Авторизация", command=self.open_login_window)
        auth_button.pack(pady=10)

        # Кнопки "Справка", "О нас", "FAQ"
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(pady=20)

        ctk.CTkButton(buttons_frame, text="Справка", command=self.show_help).pack(side="left", padx=10)
        ctk.CTkButton(buttons_frame, text="О нас", command=self.show_about).pack(side="left", padx=10)
        ctk.CTkButton(buttons_frame, text="FAQ", command=self.show_faq).pack(side="left", padx=10)

    def open_login_window(self):
        self.destroy()  # Закрываем окно приветствия
        login_window = LoginWindow()  # Открываем окно логина
        login_window.mainloop()

    def show_help(self):
        messagebox.showinfo("Справка", "Это окно справки.")

    def show_about(self):
        messagebox.showinfo("О нас", "Информация о нас.")

    def show_faq(self):
        messagebox.showinfo("FAQ", "Часто задаваемые вопросы.")


# Класс входного окна
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.geometry("400x400")
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.open_login_window()
        
    def open_login_window(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.title("Окно входа")
        self.user_entry = ctk.CTkEntry(self.main_frame, width=200, placeholder_text="Имя пользователя")
        self.user_entry.pack(pady=30)

        self.password_entry = ctk.CTkEntry(self.main_frame, show="*", width=200, placeholder_text="Пароль")
        self.password_entry.pack()

        button_frame = ctk.CTkFrame(self.main_frame)
        ctk.CTkButton(button_frame, text="Войти", command=self.login).pack(pady=5, padx=10, side="left")

        ctk.CTkButton(button_frame, text="Создать аккаунт", command=self.open_create_account_window).pack(pady=5, padx=10, side="right")
        button_frame.pack(pady=30)
    def login(self):
        username = self.user_entry.get()
        password = self.password_entry.get()
        try:
            print(username, password)
            data = db.fetch_one('''SELECT role, builder_id, id FROM Auth WHERE login = ? AND password = ?''', (username, password))
            if not data:
                return messagebox.showerror("Ошибка", "Неправильное имя пользователя или пароль")
            if data[0] == "admin":
                self.destroy()
                app = AdminWindow()
                
                app.mainloop()
            elif data[0] == "client":
                self.destroy()
                app = UserWindow(data[2])
                
                app.mainloop()
            elif data[0] == "manager":
                self.destroy()
                app = ManagerWindow()
                
                app.mainloop()
            elif data[0] == "builder":
                self.destroy()
                company = data[1]
                app = BuilderWindow(company)
                
                app.mainloop()
        except sqlite3.IntegrityError as e:
            print(e)
            messagebox.showerror("Ошибка", "Неправильное имя пользователя или пароль")

    def open_create_account_window(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.title("Создать аккаунт")
        ctk.CTkLabel(self.main_frame, text="Введите данные для создания аккаунта").pack(pady=30, padx=10)
        self.login_entry = ctk.CTkEntry(self.main_frame, width=200, placeholder_text="Имя пользователя")
        self.login_entry.pack()

        self.password_entry = ctk.CTkEntry(self.main_frame, show="*", width=200, placeholder_text="Пароль")
        self.password_entry.pack(pady=30)
        button_frame = ctk.CTkFrame(self.main_frame)
        ctk.CTkButton(button_frame, text="Создать", command=self.create_account).pack(pady=5, padx=10, side="left")
        ctk.CTkButton(button_frame, text="Вернуться ко входу", command=self.open_login_window).pack(pady=5, padx=10, side="right")
        button_frame.pack()
    def create_account(self):
        username = self.login_entry.get()
        password = self.password_entry.get()
        print(username, password)
        if username and password:
            db.execute('''INSERT INTO Auth (login, password, role) VALUES (?, ?, "user")''', (username, password))
            messagebox.showinfo("Успех", "Аккаунт создан!")
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Заполните все поля!")

class MyAppBase(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Управление недвижимостью")
        self.geometry("1200x800")
        self.theme_mode = "light"
        self.selected_property_id = None

        self.create_widgets()

    def create_widgets(self):
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(pady=20, padx=20, fill="x")

        self.switch_theme_button = ctk.CTkButton(self.top_frame, text="Переключить тему", command=self.switch_theme)
        self.switch_theme_button.pack(side="left", padx=10)

        self.exit_button = ctk.CTkButton(self.top_frame, text="Выход", command=self.return_to_login)
        self.exit_button.pack(side="right", padx=10)

    def return_to_login(self):
        self.destroy()
        login_window = LoginWindow()
        login_window.mainloop()

    def switch_theme(self):
        if self.theme_mode == "dark":
            ctk.set_appearance_mode("light")
            self.theme_mode = "light"
        else:
            ctk.set_appearance_mode("dark")
            self.theme_mode = "dark"


class AdminWindow(MyAppBase):
    def __init__(self):
        super().__init__()
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        self.home_button = ctk.CTkButton(self.top_frame, text="Главная", command=self.show_main_window)
        self.home_button.pack(side="right", padx=10)
        self.show_main_window()
    def show_main_window(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.table_frame = ctk.CTkFrame(self.main_frame)
        self.table_frame.pack(pady=10, padx=20, fill="x")
        self.operations_frame = ctk.CTkFrame(self.main_frame)
        self.operations_frame.pack(pady=10, padx=20, fill="x")
        menu_frame = ctk.CTkFrame(self.main_frame)
        menu_frame.pack(fill="both", padx=20, pady=10)
        self.sidebar_frame = ctk.CTkFrame(menu_frame, width=200)
        self.sidebar_frame.pack(side="left", padx=10, pady=10, fill="y")

        ctk.CTkLabel(self.sidebar_frame, text="Меню", font=("Calibri", 16)).pack(pady=10)
        ctk.CTkButton(self.sidebar_frame, text="Задачи", command=self.open_tasks, width=180).pack(pady=5, padx=10)
        ctk.CTkButton(self.sidebar_frame, text="Назначить роли", command=self.assign_roles, width=180).pack(pady=5, padx=10)

        self.reports_menu = ctk.CTkFrame(menu_frame, width=200)
        self.reports_menu.pack(side="left", padx=10, pady=10, fill="y")

        ctk.CTkLabel(self.reports_menu, text="Отчёты", font=("Calibri", 16)).pack(pady=10)
        ctk.CTkButton(self.reports_menu, text="Отчёт о всей недвижимости", command=self.create_estate_report, width=180).pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(self.reports_menu, text="Отчёт по недвижимости:", command=self.create_invoices_report, width=180).pack(pady=5, padx=10, fill="x")
        self.estate_id_combobox = ctk.CTkComboBox(self.reports_menu, width=180, state="readonly")
        self.estate_id_combobox.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(self.operations_frame, text="Операции с записями", font=("Calibri", 14)).pack(pady=10)
        ctk.CTkButton(self.operations_frame, text="Подробности", command=self.show_details, width=150).pack(
            side="left", padx=10)
        ctk.CTkButton(self.operations_frame, text="Добавить", command=self.show_builders, width=150).pack(
            side="left", padx=10)
        ctk.CTkButton(self.operations_frame, text="Удалить", command=self.delete_property, width=150).pack(
            side="left", padx=10)
        self.show_estate_data()
        self.fill_combobox()
    def fill_combobox(self):
        data = db.fetch('''SELECT id FROM Estate''')
        self.estate_id_combobox.configure(values=[str(row[0]) for row in data])

    def create_estate_report(self):
        from estate_report import generate_estate_report
        data = db.fetch("""
            SELECT 
                e.type AS "Тип недвижимости",
                e.location AS "Расположение",
                e.construction_date AS "Дата постройки",
                b.company_name AS "Компания",
                b.contact_number AS "Контакты"
            FROM 
                Estate e
            LEFT JOIN 
                Builders b ON e.builder_id = b.id
            LEFT JOIN 
                Appartment a ON a.estate_id = e.id
            WHERE e.status = 3
        """)
        print(data)
        generate_estate_report(data=data)

    def create_invoices_report(self):
        id = self.estate_id_combobox.get()
        if not id:
            return
        from invoices_report import create_invoices_report  
        data = db.fetch("""
        SELECT 
            a.id AS "ID квартиры",
            a.area AS "Площадь (кв.м)",
            a.rooms AS "Комнат",
            a.floor AS "Этаж",
            a.price AS "Цена (₽)",
            b.tax AS "Налог (₽)",
            CASE 
                WHEN a.sale_status = 1 THEN 'Квартира свободна'
                WHEN a.sale_status = 2 THEN 'В рассмотрении'
                WHEN a.sale_status = 3 THEN 'Квартира куплена'
            END AS "Статус"
        FROM Appartment a
        LEFT JOIN Bought_Appartments b ON a.id = b.Appartment_id
        WHERE a.estate_id = ?
        """, (id,))
        print(data)
        estate_data = db.fetch_one('''SELECT e.id, e.type, b.company_name, e.location FROM Estate e LEFT JOIN Builders b ON e.builder_id = b.id WHERE e.id = ?''', (id,))
        print(estate_data)
        create_invoices_report("invoices_report.pdf", data, estate_data)
    def show_details(self):
        if len(self.tree.selection()) == 0:
            messagebox.showwarning("Не выбрана недвижимость", "Выберите недвижимость для открытия информации")
            return
        self.selected_item = self.tree.selection()[0]
        data = self.tree.item(self.selected_item, 'values')
        estate_id = data[0]
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.info_frame = ctk.CTkFrame(self.main_frame)
        self.info_frame.pack(fill="x", pady=10)
        self.table_frame = ctk.CTkFrame(self.main_frame)
        self.table_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.show_estate_info(estate_id)
        self.show_appartment_data(estate_id)
    def show_estate_info(self, id):
        data = db.fetch_one('''SELECT Estate.type, Builders.company_name, Builders.contact_number, Estate.location, Estate.construction_date FROM Estate LEFT JOIN Builders ON Estate.builder_id = Builders.id WHERE Estate.id = ?''', (id,))
        ctk.CTkLabel(self.info_frame, text=f"Тип квартиры: {data[0]}").pack(fill="x", expand=True, side="left")
        ctk.CTkLabel(self.info_frame, text=f"Компания застройщика: {data[1]}").pack(fill="x", expand=True, side="left")
        ctk.CTkLabel(self.info_frame, text=f"Контакты застройщика: {data[2]}").pack(fill="x", expand=True, side="left")
        ctk.CTkLabel(self.info_frame, text=f"Местоположение: {data[3]}").pack(fill="x", expand=True, side="left")
        ctk.CTkLabel(self.info_frame, text=f"Дата постройки: {data[4]}").pack(fill="x", expand=True, side="left")

    def show_appartment_data(self, id):
        data = db.fetch('''SELECT id, area, rooms, floor, price, sale_status FROM Appartment WHERE estate_id = ?''', (id,))
        columns = ("id", "area", "rooms", "floor", "price", "sale_status")
        headers = ("№", "Площадь", "Количество комнат", "Этаж", "Цена", "Статус продажи")
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        for col, header in zip(columns, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=50, anchor="center")
        self.tree.pack(fill="both", expand=True)
        for row in data:
            self.tree.insert('', 'end', values=row)

    def show_estate_data(self):
        data = db.fetch('''SELECT Estate.id, Estate.type, Builders.company_name,
                        Estate.location, Estate.construction_date FROM Estate
                        LEFT JOIN Builders ON Estate.builder_id = Builders.id
                        WHERE Estate.status = 3''')
        columns = ("id", "type", "company_name", "location", "construction_date")
        headers = ("№", "Тип", "Название компании", "Локация", "Дата сооружения")
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        for col, header in zip(columns, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=50, anchor="center")
        self.tree.pack(fill="both", expand=True)
        for row in data:
            self.tree.insert('', 'end', values=row)

    def open_tasks(self):
        from todos import TodosManager
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.todos_manager = TodosManager()
        self.todo_frame = ctk.CTkScrollableFrame(self.main_frame, width=600, height=300)
        self.todo_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.input_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Введите заметку...")
        self.input_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.add_button = ctk.CTkButton(self.input_frame, text="Добавить", command=self.add_todo)
        self.add_button.pack(side="right", padx=5)
        self.load_tasks()
    def load_tasks(self):
        for widget in self.todo_frame.winfo_children():
            widget.destroy()

        todos = self.todos_manager.get_all_todos()
        for todo in todos:
            self.display_task(todo)
    def display_task(self, todo):
        task_frame = ctk.CTkFrame(self.todo_frame)
        task_frame.pack(fill="x", pady=5)

        task_text = ctk.CTkLabel(task_frame, text=f"{todo['text']}")
        task_text.pack(side="left", padx=20)
        delete_button = ctk.CTkButton(task_frame, text="Удалить", width=80, 
                                       command=lambda todo_id=todo["id"]: self.delete_task(todo_id))
        delete_button.pack(side="right", padx=5)
        status_button = ctk.CTkSegmentedButton(
            task_frame,
            values=["Создан", "В процессе", "Закончен"],
            command=lambda value, todo_id=todo["id"]: self.update_status(todo_id, value),
        )
        status_button.pack(side="right", padx=5, pady=10)
        status_button.set(self.status_text(todo["status"]))


    def add_todo(self):
        text = self.input_entry.get().strip()
        if not text:
            messagebox.showwarning("Ошибка", "Текст заметки не может быть пустым.")
            return

        new_todo = self.todos_manager.create_todo(text)
        self.input_entry.delete(0, "end")
        self.display_task(new_todo)

    def delete_task(self, todo_id):
        deleted = self.todos_manager.delete_todo(todo_id)
        if deleted:
            self.load_tasks()

    def update_status(self, todo_id, status_text):
        status_map = {"Создан": 0, "В процессе": 1, "Закончен": 2}
        self.todos_manager.update_status(todo_id, status_map[status_text])
        self.load_tasks()
    @staticmethod
    def status_text(status):
        status_map = {0: "Создан", 1: "В процессе", 2: "Закончен"}
        return status_map.get(status, "Неизвестный статус")
    
    def assign_roles(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.selected_role = ctk.StringVar(self.main_frame)
        self.table_frame = ctk.CTkFrame(self.main_frame)
        self.table_frame.pack(fill="both", expand=True, side="left")
        self.options_frame = ctk.CTkFrame(self.main_frame)
        self.options_frame.pack(side="right", fill="y", padx=10, pady=10)
        self.role_box = ctk.CTkComboBox(self.options_frame, values=["менеджер", "пользователь", "застройщик"], variable=self.selected_role, state='readonly')
        self.role_box.pack()
        
        ctk.CTkButton(self.options_frame, command=self.assign_role, text="Присвоить").pack(padx=10, pady=10)
        data = db.fetch('''SELECT id, login, role FROM Auth WHERE role IN ("manager", "builder", "user")''')
        columns = ("id", "login", "role")
        headers = ("№", "Логин", "Роль")
        self.role_translation = {
            "manager": "менеджер",
            "builder": "застройщик",
            "client": "пользователь"
        }
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        for col, header in zip(columns, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=50, anchor="center")
        self.tree.pack(fill="both", expand=True)
        for row in data:
            self.tree.insert('', 'end', values=(row[0], row[1], self.role_translation.get(row[2], "Неизвестная роль")))
        self.tree.bind("<<TreeviewSelect>>", self.select_user)

    def select_user(self, *args):
        if len(self.tree.selection()) > 0:
            self.selected_item = self.tree.selection()[0]
            data = self.tree.item(self.selected_item, 'values')
            self.selected_role.set(data[2])

    def assign_role(self):
        if len(self.tree.selection()) > 0:
            self.selected_item = self.tree.selection()[0]
            data = self.tree.item(self.selected_item, 'values')
            role = self.role_box.get()
            rev_roles = {v: k for k, v in self.role_translation.items()}
            n = rev_roles.get(role)
            db.execute('''UPDATE Auth SET role = ? WHERE id = ?''', [n, data[0]])
            self.assign_roles()

    def get_builders(self):
        data = db.fetch('''SELECT id, company_name FROM Builders''')
        self.builder_entry.set("Выберите застройщика")
        self.builder_entry.configure(values = [f"{row[0]} - {row[1]}" for row in data])
    def clear_input_fields(self):
        self.location.set("")
        self.estate_type.set("")
        self.construction_date.set("")
        self.builder.set("Выберите застройщика")


    def delete_property(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления.")
            return
        selected_item = self.tree.selection()[0]
        data = self.tree.item(self.selected_item, 'values')
        db.execute('''DELETE FROM Estate WHERE id = ?''', (data[0],))
        self.show_estate_data()
        self.clear_input_fields()

    def show_managers(self):
        pass

    def show_builders(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.frame_1 = ctk.CTkFrame(self.main_frame)
        self.frame_1.pack(fill="x")
        self.comment = ctk.StringVar(self.main_frame)
        self.table_frame = ctk.CTkFrame(self.frame_1)
        self.table_frame.pack(pady=20, padx=20, side="left", expand=True, fill="x")
        self.options_frame = ctk.CTkFrame(self.frame_1)
        self.open_details_button = ctk.CTkButton(self.options_frame, text="Подробнее", command=self.show_detailed_new_estate)
        self.open_details_button.pack(pady=5, padx=10, fill="x")
        self.accept_button = ctk.CTkButton(self.options_frame, text="Принять", command=self.accept_estate)
        self.accept_button.pack(pady=5, padx=10, fill="x")
        self.decline_button = ctk.CTkButton(self.options_frame, text="Отклонить", command=self.decline_estate)
        self.decline_button.pack(pady=5, padx=10, fill="x")
        self.options_frame.pack(side="right", padx=10)
        self.data_frame = ctk.CTkFrame(self.main_frame)
        self.comment_entry = ctk.CTkEntry(self.data_frame, textvariable=self.comment, placeholder_text="Отправьте комментарий к запросу")
        self.comment_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        self.data_frame.pack(fill="x", pady=10, padx=10)
        self.get_new_estates()
    def get_new_estates(self):
        data = db.fetch('''SELECT Estate.id, Estate.type, Builders.company_name, Estate.comment FROM Estate LEFT JOIN Builders ON Estate.builder_id = Builders.id WHERE Estate.status = 2''')
        columns = ("id", "type", "company_name", "comment")
        headers = ("№", "Тип", "Название компании", "Комментарий")
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        for col, header in zip(columns, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=50, anchor="center")
        self.tree.pack(fill="both", expand=True)
        for row in data:
            self.tree.insert('', 'end', values=row)
        self.tree.bind("<<TreeviewSelect>>", self.select_new_estate_row)
    def select_new_estate_row(self, *args):
        if len(self.tree.selection()) > 0:
            self.selected_item = self.tree.selection()[0]
            data = self.tree.item(self.selected_item, 'values')
            self.comment.set(data[3])

    def accept_estate(self):
        if len(self.tree.selection()) > 0:
            self.selected_item = self.tree.selection()[0]
            data = self.tree.item(self.selected_item, 'values')
            db.execute('''UPDATE Estate SET status = 3 WHERE id = ?''', (data[0],))
            self.show_builders()

    def decline_estate(self):
        if len(self.tree.selection()) > 0:
            self.selected_item = self.tree.selection()[0]
            comment = self.comment_entry.get()
            data = self.tree.item(self.selected_item, 'values')
            db.execute('''UPDATE Estate SET status = 4, comment = ? WHERE id = ?''', (comment, data[0]))
            self.show_builders()

    def show_detailed_new_estate(self):
        if len(self.tree.selection()) == 0:
            return
        self.selected_item = self.tree.selection()[0]
        data = self.tree.item(self.selected_item, 'values')
        id = data[0]
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.table_frame = ctk.CTkFrame(self.main_frame)
        self.table_frame.pack(pady=20, padx=20, fill="x")
        self.options_frame = ctk.CTkFrame(self.main_frame)
        self.close_button = ctk.CTkButton(self.options_frame, text="x", command=self.show_builders)
        self.close_button.pack()
        self.options_frame.pack()
        self.show_new_appartment_data(id)
    def show_new_appartment_data(self, id):
        data = db.fetch('''SELECT id, area, rooms, floor, price FROM Appartment WHERE estate_id = ?''', (id,))
        columns = ("id", "area", "rooms", "floor", "price")
        headers = ("№", "Площадь", "Количество комнат", "Этаж", "Цена")
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        for col, header in zip(columns, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=50, anchor="center")
        self.tree.pack(fill="both", expand=True)
        for row in data:
            self.tree.insert('', 'end', values=row)


class UserWindow(MyAppBase):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        self.home_button = ctk.CTkButton(self.top_frame, text="Главная", command=self.create_user_widgets)
        self.home_button.pack(side="right", padx=10)
        self.show_my_appt_button = ctk.CTkButton(self.top_frame, text="Открыть мои квартиры", command=self.show_owned_appts)
        self.show_my_appt_button.pack(side="left", padx=10)
        self.account_button = ctk.CTkButton(self.top_frame, text="Аккаунт", command=self.show_account_window)
        self.account_button.pack(side="right", padx=10)
        self.create_user_widgets()
    def create_user_widgets(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        data = db.fetch_one('''SELECT id FROM Clients WHERE user_id = ?''', (self.user_id,))
        if data:
            self.id = data[0]
            self.verified = True
        else:
            self.verified = False
        if not self.verified:
            ctk.CTkLabel(self.main_frame, text="Для запроса на покупку квартиры необходимо дополнить аккаунт сведениями").pack()
            ctk.CTkButton(self.main_frame, text="Заполнить информацию о себе", command=self.create_user_config).pack()
            self.show_my_appt_button.configure(state="disabled")
        else:
            self.show_my_appt_button.configure(state="normal")
        self.table_frame = ctk.CTkFrame(self.main_frame)
        self.table_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        self.options_frame = ctk.CTkFrame(self.main_frame)
        self.options_frame.pack(side="right", padx=10, pady=10, fill="y")
        self.submit_button = ctk.CTkButton(self.options_frame, text="Отправить запрос", command=self.send_order)
        self.submit_button.pack()
        self.show_appartment_data()
        if not self.verified:
            self.submit_button.configure(state="disabled")

    def create_user_config(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        config_frame = ctk.CTkFrame(self.main_frame)
        config_frame.pack(expand=True)
        f_1 = ctk.CTkFrame(config_frame)
        f_1.pack(fill="x")
        f_2 = ctk.CTkFrame(config_frame)
        f_2.pack(fill="x")
        f_3 = ctk.CTkFrame(config_frame)
        f_3.pack(fill="x")
        f_4 = ctk.CTkFrame(config_frame)
        f_4.pack(fill="x")
        f_5 = ctk.CTkFrame(config_frame)
        f_5.pack(pady=10)
        ctk.CTkLabel(f_1, text="Введите фамилию").pack(side="left", padx=5, pady=10)
        self.surname_entry = ctk.CTkEntry(f_1)
        self.surname_entry.pack(side="right", padx=5, pady=10)
        ctk.CTkLabel(f_2, text="Введите имя").pack(side="left", padx=5, pady=10)
        self.name_entry = ctk.CTkEntry(f_2)
        self.name_entry.pack(side="right", padx=5, pady=10)
        ctk.CTkLabel(f_3, text="Введите отчество").pack(side="left", padx=5, pady=10)
        self.patronymic_entry = ctk.CTkEntry(f_3)
        self.patronymic_entry.pack(side="right", padx=5, pady=10)
        ctk.CTkLabel(f_4, text="Введите номер телефона для связи").pack(side="left", padx=5, pady=10)
        self.number = ctk.CTkEntry(f_4)
        self.number.pack(side="right", padx=5, pady=10)
        ctk.CTkButton(f_5, command=self.save_config, text="Сохранить").pack(side="left", padx=10, pady=10)
        ctk.CTkButton(f_5, command=self.create_user_widgets, text="X").pack(side="right", padx=10, pady=10)
        
    def save_config(self):
        surname = self.surname_entry.get()
        name = self.name_entry.get()
        patronymic = self.patronymic_entry.get()
        contact_number = self.number.get()
        if not surname or not name or not patronymic or not contact_number:
            messagebox.showwarning("Не заполнены все поля", "Для сохранения необходимо заполнить все поля")
        db.execute('''INSERT INTO Clients (user_id, surname, name, patronymic, contact_number) VALUES (?, ?, ?, ?, ?)''', (self.user_id, surname, name, patronymic, contact_number))
        self.create_user_widgets()

    def show_appartment_data(self):
        data = db.fetch('''SELECT Appartment.id, Appartment.area, Appartment.rooms, Appartment.floor, Appartment.price, 
                            Estate.location FROM Appartment LEFT JOIN Estate ON Appartment.estate_id = Estate.id 
                            WHERE Appartment.sale_status = 1 AND Estate.status = 3''')
        columns = ("id", "area", "rooms", "floor", "price")
        headers = ("№", "Площадь", "Количество комнат", "Этаж", "Цена")
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        for col, header in zip(columns, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=50, anchor="center")
        self.tree.pack(fill="both", expand=True)
        for row in data:
            self.tree.insert('', 'end', values=row)

    def send_order(self):
        if len(self.tree.selection()) == 0:
            messagebox.showwarning("Не выбрана квартира для отправки запроса")
            return
        self.selected_item = self.tree.selection()[0]
        data = self.tree.item(self.selected_item, 'values')
        db.execute('''INSERT INTO Orders (client_id, appartment_id) VALUES (?, ?)''', (self.id, data[0]))
        db.execute('''UPDATE Appartment SET sale_status = 2 WHERE id = ?''', (data[0]))
        self.create_user_widgets()

    def show_account_window(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        account_frame = ctk.CTkFrame(self.main_frame)
        account_frame.pack(expand=True)
        data = db.fetch_one('''SELECT surname, name, patronymic, contact_number
                            FROM Clients WHERE user_id = ?''', (self.user_id,))
        if not data:
            ctk.CTkLabel(account_frame, text="Заполните данные об аккаунте").pack(pady=10, padx=10)
            ctk.CTkButton(account_frame, command=self.create_user_config, text="Заполнить").pack(pady=10, padx=10)
        else:
            ctk.CTkLabel(account_frame, text=f"Фамилия: {data[0]}").pack(pady=10, padx=10)
            ctk.CTkLabel(account_frame, text=f"Имя: {data[1]}").pack(pady=10, padx=10)
            ctk.CTkLabel(account_frame, text=f"Отчество: {data[2]}").pack(pady=10, padx=10)
            ctk.CTkLabel(account_frame, text=f"Контактный номер: {data[3]}").pack(pady=10, padx=10)
        ctk.CTkButton(account_frame, command=self.create_user_widgets, text="X").pack(padx=10, pady=10)

    def show_owned_appts(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        owned_table = ctk.CTkFrame(self.main_frame)
        owned_table.pack(expand=True)
        data = db.fetch('''SELECT Appartment.id, Appartment.area,
                        Bought_Appartments.purchase_date, Bought_Appartments.tax
                        FROM Bought_Appartments LEFT JOIN Appartment ON
                        Bought_Appartments.Appartment_id = Appartment.id
                        WHERE Bought_Appartments.owner_id = ?''', (self.id,))
        for row in data:
            ctk.CTkLabel(owned_table, text=f"{row[0]}: площадь - {row[1]}, дата покупки - {row[2]}, размер платы - {row[3]}").pack(pady=10, padx=20)

class BuilderWindow(MyAppBase):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.builder_mode = True
        self.main_frame = ctk.CTkFrame(self)
        
        self.main_frame.pack(fill="both", expand=True)
        self.home_button = ctk.CTkButton(self.top_frame, text="Главная", command=self.create_builder_widgets)
        self.home_button.pack(side="right", padx=10)
        self.create_builder_widgets()

    def create_builder_widgets(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.comments_dict = {}
        self.comment = ctk.StringVar(self.main_frame)

        self.table_frame = ctk.CTkFrame(self.main_frame)
        self.table_frame.pack(fill="both", pady=10, expand=True)

        self.operations_frame = ctk.CTkFrame(self.main_frame)
        self.operations_frame.pack(pady=20, padx=20)

        self.add_button = ctk.CTkButton(self.operations_frame, text="Добавить недвижимость", command=self.add_estate_menu, width=200)
        self.add_button.pack(side="left", padx=10, pady=10)
        self.open_button = ctk.CTkButton(self.operations_frame, text="Открыть недвижимость", command=self.open_estate, width=200)
        self.open_button.pack(side="left", padx=10, pady=10)
        self.send_button = ctk.CTkButton(self.operations_frame, text="Отправить на проверку", command=self.send_to_admin, width=200)
        self.send_button.pack(side="left", padx=10, pady=10)
        comment_frame = ctk.CTkFrame(self.main_frame)
        comment_frame.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(comment_frame, text="Комментарий").pack(padx=20, pady=5, side="left")
        self.comment_entry = ctk.CTkEntry(comment_frame, textvariable=self.comment)
        self.comment_entry.pack(side="left", padx=30, fill="x", expand=True, pady=20)
        self.show_estate_queries()

    def show_estate_queries(self):
        status_map = {
            1: "Создан",
            2: "На проверке",
            4: "Возвращен"
        }
        data = db.fetch('''SELECT Estate.id, Estate.type, Estate.location, Estate.construction_date,
                            Estate.status, Estate.comment 
                            FROM Estate 
                            WHERE Estate.builder_id = ? AND Estate.status IN (1, 2, 4)''', (self.id,))
        columns = ("id", "type", "location", "construction_date", "status")
        headers = ("№", "Тип", "Локация", "Дата сооружения", "Статус")
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        for col, header in zip(columns, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=50, anchor="center")
        self.tree.pack(fill="both", expand=True)
        for row in data:
            estate_id, estate_type, location, construction_date, status, comment = row
            if comment != None:
                self.comments_dict[f"id_{estate_id}"] = comment
            status_text = status_map.get(status, "Неизвестен")
            self.tree.insert('', 'end', values=(estate_id, estate_type, location, construction_date, status_text))
            self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)

    def on_item_selected(self, event):
        if len(self.tree.selection()) > 0:
            self.selected_item = self.tree.selection()[0]
            data = self.tree.item(self.selected_item, 'values')
            print(self.comments_dict)
            print(data[0])
            comment = self.comments_dict.get(f"id_{data[0]}", "")
            print(comment)
            self.comment.set(comment)
            if data[4] == "На проверке":
                self.comment_entry.configure(state="disabled")
                self.send_button.configure(state="disabled")
            else:
                self.comment_entry.configure(state="normal")
                self.send_button.configure(state="normal")

    def send_to_admin(self):
        if len(self.tree.selection()) > 0:
            self.selected_item = self.tree.selection()[0]
            data = self.tree.item(self.selected_item, 'values')
            db.execute('''UPDATE Estate SET status = 2, comment = ? WHERE id = ?''', (self.comment.get(), data[0]))
            self.create_builder_widgets()

    def add_estate_menu(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.type = ctk.StringVar(self.main_frame)
        self.location = ctk.StringVar(self.main_frame)
        self.date = ctk.StringVar(self.main_frame)
        add_frame = ctk.CTkFrame(self.main_frame)
        add_frame.pack(expand=True)
        ctk.CTkLabel(add_frame, text="Введите тип недвижимости").pack(padx=10, pady=5)
        ctk.CTkEntry(add_frame, textvariable=self.type).pack(padx=10, pady=5)
        ctk.CTkLabel(add_frame, text="Введите местоположение недвижимости").pack(padx=10, pady=5)
        ctk.CTkEntry(add_frame, textvariable=self.location).pack(padx=10, pady=5)
        ctk.CTkLabel(add_frame, text="Введите дату постройки недвижимости в формате: День-Месяц-Год").pack(padx=10, pady=5)
        ctk.CTkEntry(add_frame, textvariable=self.date).pack(padx=10, pady=5)
        button_frame = ctk.CTkFrame(add_frame)
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, command=self.add_estate, text="Добавить").pack(side="left", padx=10, pady=10)
    def open_estate(self):
        if len(self.tree.selection()) == 0:
            messagebox.showwarning("Не выбрана недвижимость", "Выберите недвижимость для детальной информации")
            return
        self.selected_item = self.tree.selection()[0]
        data = self.tree.item(self.selected_item, 'values')
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        data_frame = ctk.CTkFrame(self.main_frame)
        if data[4] != "На проверке":
            data_frame.pack(fill="x")
        self.estate_id = data[0]
        self.type = ctk.StringVar(self.main_frame, value=data[1])
        self.location = ctk.StringVar(self.main_frame, value=data[2])
        self.date = ctk.StringVar(self.main_frame, value=data[3])

        self.area = ctk.StringVar(self.main_frame)
        self.rooms = ctk.StringVar(self.main_frame)
        self.floor = ctk.StringVar(self.main_frame)
        self.price = ctk.StringVar(self.main_frame)

        f_1 = ctk.CTkFrame(data_frame)
        f_1.pack(pady=10, fill="x")
        f_2 = ctk.CTkFrame(data_frame)
        f_2.pack(pady=10, fill="x")
        f_3 = ctk.CTkFrame(data_frame)
        f_3.pack(pady=10, fill="x")
        ctk.CTkLabel(f_1, text="Тип недвижимости: ").pack(side="left", padx=10, pady=5)
        ctk.CTkEntry(f_1, textvariable=self.type).pack(side="right", padx=10, pady=5)
        ctk.CTkLabel(f_2, text="Местоположение недвижимости: ").pack(side="left", padx=10, pady=5)
        ctk.CTkEntry(f_2, textvariable=self.location).pack(side="right", padx=10, pady=5)
        ctk.CTkLabel(f_3, text="Дата постройки: ").pack(side="left", padx=10, pady=5)
        ctk.CTkEntry(f_3, textvariable=self.date).pack(side="right", padx=10, pady=5)
        save_button = ctk.CTkButton(data_frame, command=self.save_estate_data, text="Сохранить")
        if data[4] != "На проверке":
            save_button.pack(padx=10, pady=10)
        self.table_frame = ctk.CTkFrame(self.main_frame)
        self.table_frame.pack(fill="both", side="left", expand="True")
        self.appartment_options = ctk.CTkFrame(self.main_frame)
        if data[4] != "На проверке":
            self.appartment_options.pack(fill="both", side="right", expand="True")
        f_1 = ctk.CTkFrame(self.appartment_options)
        f_1.pack(fill="x", padx=30, pady=10)
        f_2 = ctk.CTkFrame(self.appartment_options)
        f_2.pack(fill="x", padx=30, pady=10)
        f_3 = ctk.CTkFrame(self.appartment_options)
        f_3.pack(fill="x", padx=30, pady=10)
        f_4 = ctk.CTkFrame(self.appartment_options)
        f_4.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(f_1, text="Площадь: ").pack(fill="x", padx=10, side="left", expand=True)
        ctk.CTkEntry(f_1, textvariable=self.area).pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(f_2, text="Количество комнат: ").pack(fill="x", padx=10, side="left", expand=True)
        ctk.CTkEntry(f_2, textvariable=self.rooms).pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(f_3, text="Этаж: ").pack(fill="x", padx=10, side="left", expand=True)
        ctk.CTkEntry(f_3, textvariable=self.floor).pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(f_4, text="Цена: ").pack(fill="x", padx=10, side="left", expand=True)
        ctk.CTkEntry(f_4, textvariable=self.price).pack(fill="x", padx=10, pady=5)
        appartment_buttons_frame = ctk.CTkFrame(self.appartment_options)
        appartment_buttons_frame.pack(pady=10)
        ctk.CTkButton(appartment_buttons_frame, command=self.add_appartment, text="Добавить квартиру").pack(side="left", padx=10, pady=10)
        ctk.CTkButton(appartment_buttons_frame, command=self.edit_appartment, text="Изменить квартиру").pack(side="left", padx=10, pady=10)
        ctk.CTkButton(appartment_buttons_frame, command=self.delete_appartment, text="Удалить квартиру").pack(side="left", padx=10, pady=10)
        self.show_appartment_data()
    def save_estate_data(self):
        type = self.type.get()
        location = self.location.get()
        date = self.date.get()
        if not type or not location or not date:
            messagebox.showerror("Ошибка", "Введите все данные")
            return
        if re.match(r"^\d{2}-\d{2}-\d{4}$", date):
            try:
                date_obj = datetime.strptime(date, "%d-%m-%Y")
                formatted_date = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректная дата")
                return
        else:
            messagebox.showerror("Ошибка", "Введите дату в правильном формате")
            return
        db.execute('''UPDATE Estate SET type = ?, location = ?, construction_date = ? WHERE id = ?''', (type, location, date, self.estate_id))
    def show_appartment_data(self):
        data = db.fetch('''SELECT id, area, rooms, floor, price FROM Appartment WHERE estate_id = ?''', (self.estate_id,))
        columns = ("id", "area", "rooms", "floor", "price")
        headers = ("№", "Площадь", "Количество комнат", "Этаж", "Цена")
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        for col, header in zip(columns, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=50, anchor="center")
        self.tree.pack(fill="both", expand=True)
        for row in data:
            self.tree.insert('', 'end', values=row)
        self.tree.bind("<<TreeviewSelect>>", self.select_appartment)

    def add_estate(self):
        type = self.type.get()
        location = self.location.get()
        date = self.date.get()
        if not type or not location or not date:
            messagebox.showerror("Ошибка", "Введите все данные")
            return
        if re.match(r"^\d{2}-\d{2}-\d{4}$", date):
            try:
                date_obj = datetime.strptime(date, "%d-%m-%Y")
                formatted_date = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректная дата")
                return
        else:
            messagebox.showerror("Ошибка", "Введите дату в правильном формате")
            return
        db.execute('''INSERT INTO Estate (type, builder_id, location, construction_date, status) VALUES (?, ?, ?, ?, 1)''', (type, self.id, location, date))
        self.create_builder_widgets()

    def add_appartment(self):
        area = self.area.get()
        rooms = self.rooms.get()
        floor = self.floor.get()
        price = self.price.get()
        if not area or not rooms or not floor or not price:
            messagebox.showerror("Ошибка", "Введите все данные")
            return
        try:
            area = float(area)
            price = float(price)
            rooms = int(rooms)
            floor = int(floor)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые данные")
            return
        db.execute('''INSERT INTO Appartment (area, rooms, floor, price, sale_status, estate_id) VALUES (?, ?, ?, ?, 1, ?)''', (area, rooms, floor, price, self.estate_id))
        self.show_appartment_data()

    def edit_appartment(self):
        if len(self.tree.selection()) == 0:
            messagebox.showwarning("Не выбрана квартира", "Выберите квартиру для изменения")
            return
        self.selected_item = self.tree.selection()[0]
        data = self.tree.item(self.selected_item, 'values')
        area = self.area.get()
        rooms = self.rooms.get()
        floor = self.floor.get()
        price = self.price.get()
        if not area or not rooms or not floor or not price:
            messagebox.showerror("Ошибка", "Введите все данные")
            return
        try:
            area = float(area)
            price = float(price)
            rooms = int(rooms)
            floor = int(floor)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые данные")
            return
        db.execute('''UPDATE Appartment SET area = ?, rooms = ?, floor = ?, price = ? WHERE id = ?''', (area, rooms, floor, price, data[0]))
        self.show_appartment_data()    
    def delete_appartment(self):
        if len(self.tree.selection()) == 0:
            messagebox.showwarning("Не выбрана квартира", "Выберите квартиру для удаления")
            return
        self.selected_item = self.tree.selection()[0]
        data = self.tree.item(self.selected_item, 'values')
        db.execute('''DELETE FROM Appartment WHERE id = ?''', (data[0],))
        self.show_appartment_data()
    def select_appartment(self, *args):
        if len(self.tree.selection()) == 0:
            return
        self.selected_item = self.tree.selection()[0]
        data = self.tree.item(self.selected_item, 'values')
        self.area.set(data[1])
        self.rooms.set(data[2])
        self.floor.set(data[3])
        self.price.set(data[4])

class ManagerWindow(MyAppBase):
    def __init__(self):
        super().__init__()
        self.title("Менеджер")
        self.geometry("800x600")
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        reports_menu = ctk.CTkFrame(self.main_frame)
        reports_menu.pack(fill="both", padx=10, pady=10, expand=True)

        reports_label = ctk.CTkLabel(reports_menu, text="Запросы на покупку")
        reports_label.pack(pady=5)
        self.table_frame = ctk.CTkFrame(reports_menu)
        self.table_frame.pack(fill="both", expand=True)
        button_frame = ctk.CTkFrame(reports_menu)
        button_frame.pack()
        ctk.CTkButton(button_frame, text="Одобрить", command=self.submit_deal).pack(side="left", pady=5, padx=10)
        ctk.CTkButton(button_frame, text="Создать отчёт", command=self.generate_report).pack(side="right", pady=5, padx=10)
        self.show_appartment_data()
    def generate_report(self):
        from appartment_report import generate_report
        data = db.fetch("""
        SELECT 
            b.id AS "№ сделки",
            a.area AS "Площадь (кв.м)",
            a.rooms AS "Комнат",
            a.floor AS "Этаж",
            a.price AS "Цена (₽)",
            b.tax AS "Налог (₽)",
            b.purchase_price AS "Цена покупки (₽)",
            b.purchase_date AS "Дата покупки"
        FROM Bought_Appartments b
        JOIN Appartment a ON b.Appartment_id = a.id
        """)
        headers = ["№ сделки", "Площадь (кв.м)", "Комнат", "Этаж", "Цена (₽)", "Налог (₽)", "Цена покупки (₽)", "Дата покупки"]
        table_data = [headers] + data
        total_tax = sum(row[5] for row in data)
        generate_report("appartment_report.pdf", table_data, total_tax)

    def show_appartment_data(self):
        data = db.fetch('''SELECT Orders.id, Clients.surname, Clients.contact_number,
                        Appartment.area, Appartment.floor, Appartment.price
                        FROM Orders LEFT JOIN Clients ON Orders.client_id = Clients.id
                        LEFT JOIN Appartment ON Orders.appartment_id = Appartment.id''')
        columns = ("id", "surname", "contact_number", "area", "floor", "price")
        headers = ("№", "Фамилия", "Номер телефона", "Площадь", "Этаж", "Цена")
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        for col, header in zip(columns, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=50, anchor="center")
        self.tree.pack(fill="both", expand=True)
        for row in data:
            self.tree.insert('', 'end', values=row)

    def submit_deal(self):
        if len(self.tree.selection()) == 0:
            return
        self.selected_item = self.tree.selection()[0]
        data = self.tree.item(self.selected_item, 'values')
        orders = db.fetch_one('''SELECT client_id, appartment_id FROM Orders WHERE id = ?''', (data[0],))
        price = data[5]
        tax = float(price) * 0.001
        date = datetime.now()
        formatted_date = date.strftime("%Y-%m-%d")
        db.execute('''DELETE FROM Orders WHERE id = ?''', (data[0],))
        db.execute('''UPDATE Appartment SET sale_status = 3 WHERE id = ?''', (orders[1],))
        db.execute('''INSERT INTO Bought_Appartments
                   (Appartment_id, owner_id, purchase_date, tax, purchase_price)
                   VALUES (?, ?, ?, ?, ?)''', (orders[1], orders[0], formatted_date, tax, price))
        self.show_appartment_data()

class App():
    def __init__(self):
        global db
        db = Database()
        # first_page = BuilderWindow(3)
        # first_page = AdminWindow()
        # first_page = ManagerWindow()
        first_page = WelcomePage()
        # first_page = UserWindow(7)
        ctk.set_appearance_mode("light")
        first_page.mainloop()

if __name__ == "__main__":
    app = App()

