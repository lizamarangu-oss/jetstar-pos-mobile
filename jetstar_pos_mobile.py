#!/usr/bin/env python3
"""
JETSTAR POS - Android Mobile App (Kivy) - Simplified & Robust
Can be built into Android APK using buildozer
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
import sqlite3
from datetime import datetime
from pathlib import Path

Window.clearcolor = (0.96, 0.96, 0.96, 1)

class Database:
    def __init__(self):
        db_dir = Path.home() / '.jetstarpos'
        db_dir.mkdir(exist_ok=True)
        self.db_path = db_dir / 'mobile.db'
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_tables()
    
    def init_tables(self):
        cursor = self.conn.cursor()
        tables = [
            '''CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT UNIQUE,
                date DATE,
                customer_id INTEGER,
                amount REAL,
                payment_method TEXT,
                status TEXT DEFAULT 'completed',
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sku TEXT UNIQUE,
                category TEXT,
                quantity INTEGER DEFAULT 0,
                unit_cost REAL,
                selling_price REAL,
                type TEXT DEFAULT 'product',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                credit_limit REAL DEFAULT 0,
                balance REAL DEFAULT 0
            )''',
            '''CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                balance REAL DEFAULT 0
            )''',
            '''CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                category TEXT,
                description TEXT,
                vendor TEXT,
                amount REAL,
                reference TEXT
            )'''
        ]
        for table_sql in tables:
            cursor.execute(table_sql)
        self.conn.commit()
    
    def get_sales(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM sales ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]
    
    def add_sale(self, reference, date, customer_id, amount, payment_method, notes=''):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO sales (reference, date, customer_id, amount, payment_method, notes)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (reference, date, customer_id, amount, payment_method, notes))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_stock(self, stock_type='product'):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM stock WHERE type = ? ORDER BY name', (stock_type,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_customers(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM customers ORDER BY name')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_expenses(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM expenses ORDER BY date DESC')
        return [dict(row) for row in cursor.fetchall()]


class DashboardScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # Header
        header = BoxLayout(size_hint_y=0.12, spacing=10)
        title = Label(text='[b]JETSTAR POS[/b]', font_size='28sp', markup=True,
                     color=(0.18, 0.31, 0.09, 1))
        new_sale_btn = Button(text='+ New Sale', size_hint_x=0.35, 
                             background_color=(0.18, 0.31, 0.09, 1), 
                             color=(1, 1, 1, 1), bold=True, font_size='16sp')
        new_sale_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'sell'))
        header.add_widget(title)
        header.add_widget(new_sale_btn)
        layout.add_widget(header)
        
        # Stats
        stats_grid = GridLayout(cols=2, spacing=15, size_hint_y=0.28)
        
        sales = self.db.get_sales()
        expenses = self.db.get_expenses()
        stock = self.db.get_stock()
        
        total_sales = sum(float(s.get('amount', 0)) for s in sales)
        total_expenses = sum(float(e.get('amount', 0)) for e in expenses)
        
        # Sales card
        sales_card = self.create_stat_card('Sales', f'${total_sales:.2f}', 
                                           (0.3, 0.69, 0.31, 1))
        stats_grid.add_widget(sales_card)
        
        # Stock card
        stock_card = self.create_stat_card('Stock Items', str(len(stock)), 
                                           (0.13, 0.59, 0.95, 1))
        stats_grid.add_widget(stock_card)
        
        layout.add_widget(stats_grid)
        
        # Quick Actions
        actions_label = Label(text='[b]Quick Actions[/b]', font_size='22sp', 
                             markup=True, size_hint_y=0.08, 
                             color=(0.2, 0.2, 0.2, 1), halign='left')
        actions_label.bind(size=actions_label.setter('text_size'))
        layout.add_widget(actions_label)
        
        actions_grid = GridLayout(cols=2, spacing=15, size_hint_y=0.52)
        
        actions = [
            ('New Sale', 'sell', (0.3, 0.69, 0.31, 1)),
            ('View Stock', 'stock', (0.13, 0.59, 0.95, 1)),
            ('Add Expense', 'expenses', (0.96, 0.26, 0.21, 1)),
            ('Reports', 'reports', (1, 0.6, 0, 1))
        ]
        
        for text, screen, color in actions:
            btn = Button(text=text, background_color=color, color=(1, 1, 1, 1), 
                        font_size='20sp', bold=True)
            btn.bind(on_press=lambda x, s=screen: setattr(self.manager, 'current', s))
            actions_grid.add_widget(btn)
        
        layout.add_widget(actions_grid)
        self.add_widget(layout)
    
    def create_stat_card(self, title, value, color):
        card = BoxLayout(orientation='vertical', padding=20, spacing=8)
        
        # Add rounded background
        with card.canvas.before:
            Color(1, 1, 1, 1)
            card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
        card.bind(pos=lambda *args: setattr(card.rect, 'pos', card.pos))
        card.bind(size=lambda *args: setattr(card.rect, 'size', card.size))
        
        card.add_widget(Label(text=title, color=(0.5, 0.5, 0.5, 1), 
                             font_size='16sp', size_hint_y=0.3))
        card.add_widget(Label(text=value, font_size='38sp', bold=True, 
                             color=color, size_hint_y=0.7))
        return card


class SellScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.cart = []
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='horizontal', padding=15, spacing=15)
        
        # Left - Products
        left_panel = BoxLayout(orientation='vertical', spacing=10, size_hint_x=0.55)
        
        left_panel.add_widget(Label(text='[b]Products[/b]', markup=True,
                                   font_size='24sp', size_hint_y=0.08, 
                                   color=(0.2, 0.2, 0.2, 1)))
        
        # Search
        self.search_input = TextInput(hint_text='Search products...', multiline=False, 
                                     size_hint_y=0.08, font_size='16sp')
        self.search_input.bind(text=self.filter_products)
        left_panel.add_widget(self.search_input)
        
        # Products list
        self.products_scroll = ScrollView(size_hint_y=0.84)
        self.products_layout = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=5)
        self.products_layout.bind(minimum_height=self.products_layout.setter('height'))
        self.products_scroll.add_widget(self.products_layout)
        left_panel.add_widget(self.products_scroll)
        
        self.load_products()
        
        # Right - Cart
        right_panel = BoxLayout(orientation='vertical', spacing=10, size_hint_x=0.45)
        
        right_panel.add_widget(Label(text='[b]Cart[/b]', markup=True,
                                    font_size='24sp', size_hint_y=0.06, 
                                    color=(0.2, 0.2, 0.2, 1)))
        
        self.cart_scroll = ScrollView(size_hint_y=0.52)
        self.cart_layout = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=5)
        self.cart_layout.bind(minimum_height=self.cart_layout.setter('height'))
        self.cart_scroll.add_widget(self.cart_layout)
        right_panel.add_widget(self.cart_scroll)
        
        # Total
        self.total_label = Label(text='[b]Total: $0.00[/b]', markup=True,
                                font_size='32sp', size_hint_y=0.1, 
                                color=(0.3, 0.69, 0.31, 1))
        right_panel.add_widget(self.total_label)
        
        # Buttons
        checkout_btn = Button(text='Complete Sale', size_hint_y=0.12, 
                            background_color=(0.15, 0.39, 0.58, 1), 
                            color=(1, 1, 1, 1), font_size='20sp', bold=True)
        checkout_btn.bind(on_press=self.checkout)
        right_panel.add_widget(checkout_btn)
        
        clear_btn = Button(text='Clear Cart', size_hint_y=0.1, 
                          background_color=(0.96, 0.26, 0.21, 1), 
                          color=(1, 1, 1, 1), font_size='16sp')
        clear_btn.bind(on_press=lambda x: self.clear_cart())
        right_panel.add_widget(clear_btn)
        
        back_btn = Button(text='← Back to Dashboard', size_hint_y=0.1, 
                         background_color=(0.5, 0.5, 0.5, 1), 
                         color=(1, 1, 1, 1), font_size='16sp')
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        right_panel.add_widget(back_btn)
        
        main_layout.add_widget(left_panel)
        main_layout.add_widget(right_panel)
        self.add_widget(main_layout)
    
    def load_products(self):
        self.products_layout.clear_widgets()
        products = self.db.get_stock()
        
        if not products:
            self.products_layout.add_widget(
                Label(text='No products found. Add some products first!', 
                      color=(0.6, 0.6, 0.6, 1), font_size='16sp', size_hint_y=None, height=100))
            return
        
        for product in products:
            product_box = BoxLayout(orientation='horizontal', size_hint_y=None, 
                                   height=70, padding=12, spacing=10)
            
            with product_box.canvas.before:
                Color(1, 1, 1, 1)
                product_box.rect = RoundedRectangle(pos=product_box.pos, 
                                                    size=product_box.size, radius=[8])
            product_box.bind(pos=lambda *args, pb=product_box: setattr(pb.rect, 'pos', pb.pos))
            product_box.bind(size=lambda *args, pb=product_box: setattr(pb.rect, 'size', pb.size))
            
            info_layout = BoxLayout(orientation='vertical')
            name = str(product.get('name', 'Unknown'))
            price = float(product.get('selling_price', 0))
            qty = int(product.get('quantity', 0))
            
            info_layout.add_widget(Label(text=f'[b]{name}[/b]', markup=True,
                                        color=(0.2, 0.2, 0.2, 1), font_size='17sp',
                                        halign='left', valign='middle'))
            info_layout.add_widget(Label(text=f'${price:.2f} • Stock: {qty}', 
                                        color=(0.5, 0.5, 0.5, 1), font_size='14sp',
                                        halign='left', valign='middle'))
            
            for widget in info_layout.children:
                widget.bind(size=widget.setter('text_size'))
            
            add_btn = Button(text='+', size_hint_x=0.18, 
                           background_color=(0.3, 0.69, 0.31, 1),
                           font_size='24sp', bold=True)
            add_btn.bind(on_press=lambda x, p=product: self.add_to_cart(p))
            
            product_box.add_widget(info_layout)
            product_box.add_widget(add_btn)
            self.products_layout.add_widget(product_box)
    
    def filter_products(self, instance, value):
        self.load_products()
    
    def add_to_cart(self, product):
        product_id = int(product.get('id', 0))
        existing = next((item for item in self.cart if item['id'] == product_id), None)
        
        if existing:
            existing['qty'] += 1
        else:
            self.cart.append({
                'id': product_id,
                'name': str(product.get('name', 'Unknown')),
                'price': float(product.get('selling_price', 0)),
                'qty': 1
            })
        self.update_cart()
    
    def update_cart(self):
        self.cart_layout.clear_widgets()
        total = 0
        
        if not self.cart:
            self.cart_layout.add_widget(
                Label(text='Cart is empty', color=(0.6, 0.6, 0.6, 1), 
                      font_size='16sp', size_hint_y=None, height=60))
            self.total_label.text = '[b]Total: $0.00[/b]'
            return
        
        for item in self.cart:
            qty = int(item['qty'])
            price = float(item['price'])
            subtotal = price * qty
            total += subtotal
            
            cart_item = BoxLayout(size_hint_y=None, height=65, padding=8, spacing=8)
            
            with cart_item.canvas.before:
                Color(0.95, 0.95, 0.95, 1)
                cart_item.rect = RoundedRectangle(pos=cart_item.pos, 
                                                  size=cart_item.size, radius=[6])
            cart_item.bind(pos=lambda *args, ci=cart_item: setattr(ci.rect, 'pos', ci.pos))
            cart_item.bind(size=lambda *args, ci=cart_item: setattr(ci.rect, 'size', ci.size))
            
            name = str(item['name'])[:20]
            info_label = Label(text=f'[b]{name}[/b]\n${price:.2f} × {qty}', 
                              markup=True, color=(0.2, 0.2, 0.2, 1), 
                              font_size='14sp', halign='left', valign='middle')
            info_label.bind(size=info_label.setter('text_size'))
            
            subtotal_label = Label(text=f'[b]${subtotal:.2f}[/b]', markup=True,
                                  bold=True, color=(0.3, 0.69, 0.31, 1), 
                                  size_hint_x=0.25, font_size='16sp')
            
            remove_btn = Button(text='×', size_hint_x=0.12, 
                              background_color=(0.96, 0.26, 0.21, 1),
                              font_size='22sp', bold=True)
            remove_btn.bind(on_press=lambda x, i=item: self.remove_from_cart(i))
            
            cart_item.add_widget(info_label)
            cart_item.add_widget(subtotal_label)
            cart_item.add_widget(remove_btn)
            self.cart_layout.add_widget(cart_item)
        
        self.total_label.text = f'[b]Total: ${total:.2f}[/b]'
    
    def remove_from_cart(self, item):
        self.cart = [i for i in self.cart if i['id'] != item['id']]
        self.update_cart()
    
    def clear_cart(self):
        self.cart.clear()
        self.update_cart()
    
    def checkout(self, instance):
        if not self.cart:
            return
        
        total = sum(float(item['price']) * int(item['qty']) for item in self.cart)
        reference = f"SALE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        date = datetime.now().strftime('%Y-%m-%d')
        
        self.db.add_sale(reference, date, None, total, 'Cash', '')
        
        self.cart.clear()
        self.update_cart()
        self.manager.current = 'dashboard'


class StockScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.1)
        header.add_widget(Label(text='[b]Stock Management[/b]', markup=True,
                               font_size='26sp', color=(0.2, 0.2, 0.2, 1)))
        back_btn = Button(text='← Back', size_hint_x=0.25, 
                         background_color=(0.5, 0.5, 0.5, 1), 
                         color=(1, 1, 1, 1), font_size='16sp')
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        header.add_widget(back_btn)
        layout.add_widget(header)
        
        # Stock list
        scroll = ScrollView()
        content = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=5)
        content.bind(minimum_height=content.setter('height'))
        
        products = self.db.get_stock()
        
        if not products:
            content.add_widget(Label(text='No stock items found', 
                                    color=(0.6, 0.6, 0.6, 1), font_size='18sp',
                                    size_hint_y=None, height=100))
        else:
            for product in products:
                item_box = BoxLayout(size_hint_y=None, height=75, padding=15, spacing=10)
                
                with item_box.canvas.before:
                    Color(1, 1, 1, 1)
                    item_box.rect = RoundedRectangle(pos=item_box.pos, 
                                                     size=item_box.size, radius=[10])
                item_box.bind(pos=lambda *args, ib=item_box: setattr(ib.rect, 'pos', ib.pos))
                item_box.bind(size=lambda *args, ib=item_box: setattr(ib.rect, 'size', ib.size))
                
                name = str(product.get('name', 'Unknown'))
                sku = str(product.get('sku', 'N/A'))
                price = float(product.get('selling_price', 0))
                qty = int(product.get('quantity', 0))
                
                info_label = Label(text=f'[b]{name}[/b]\nSKU: {sku}', 
                                  markup=True, color=(0.2, 0.2, 0.2, 1), 
                                  font_size='16sp', halign='left', valign='middle')
                info_label.bind(size=info_label.setter('text_size'))
                
                stats_label = Label(text=f'[b]${price:.2f}[/b]\nQty: {qty}', 
                                   markup=True, color=(0.3, 0.69, 0.31, 1), 
                                   size_hint_x=0.3, font_size='15sp')
                
                item_box.add_widget(info_label)
                item_box.add_widget(stats_label)
                content.add_widget(item_box)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)


class ExpensesScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        header = BoxLayout(size_hint_y=0.1)
        header.add_widget(Label(text='[b]Expenses[/b]', markup=True,
                               font_size='26sp', color=(0.2, 0.2, 0.2, 1)))
        back_btn = Button(text='← Back', size_hint_x=0.25, 
                         background_color=(0.5, 0.5, 0.5, 1), 
                         color=(1, 1, 1, 1), font_size='16sp')
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        header.add_widget(back_btn)
        layout.add_widget(header)
        
        expenses = self.db.get_expenses()
        total = sum(float(e.get('amount', 0)) for e in expenses)
        
        layout.add_widget(Label(text=f'[b]Total: ${total:.2f}[/b]', markup=True,
                               font_size='24sp', size_hint_y=0.08, 
                               color=(0.96, 0.26, 0.21, 1)))
        
        scroll = ScrollView()
        content = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=5)
        content.bind(minimum_height=content.setter('height'))
        
        if not expenses:
            content.add_widget(Label(text='No expenses recorded', 
                                    color=(0.6, 0.6, 0.6, 1), font_size='18sp',
                                    size_hint_y=None, height=100))
        else:
            for expense in expenses:
                item = BoxLayout(size_hint_y=None, height=70, padding=15, spacing=10)
                
                with item.canvas.before:
                    Color(1, 1, 1, 1)
                    item.rect = RoundedRectangle(pos=item.pos, size=item.size, radius=[10])
                item.bind(pos=lambda *args, i=item: setattr(i.rect, 'pos', i.pos))
                item.bind(size=lambda *args, i=item: setattr(i.rect, 'size', i.size))
                
                desc = str(expense.get('description', 'N/A'))
                date_str = str(expense.get('date', ''))
                amt = float(expense.get('amount', 0))
                
                info_label = Label(text=f'[b]{desc}[/b]\n{date_str}', markup=True,
                                  color=(0.2, 0.2, 0.2, 1), font_size='15sp',
                                  halign='left', valign='middle')
                info_label.bind(size=info_label.setter('text_size'))
                
                amt_label = Label(text=f'[b]${amt:.2f}[/b]', markup=True,
                                 color=(0.96, 0.26, 0.21, 1), size_hint_x=0.3,
                                 font_size='18sp')
                
                item.add_widget(info_label)
                item.add_widget(amt_label)
                content.add_widget(item)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)


class ReportsScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        header = BoxLayout(size_hint_y=0.1)
        header.add_widget(Label(text='[b]Sales Report[/b]', markup=True,
                               font_size='26sp', color=(0.2, 0.2, 0.2, 1)))
        back_btn = Button(text='← Back', size_hint_x=0.25, 
                         background_color=(0.5, 0.5, 0.5, 1), 
                         color=(1, 1, 1, 1), font_size='16sp')
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        header.add_widget(back_btn)
        layout.add_widget(header)
        
        sales = self.db.get_sales()
        expenses = self.db.get_expenses()
        
        total_sales = sum(float(s.get('amount', 0)) for s in sales)
        total_expenses = sum(float(e.get('amount', 0)) for e in expenses)
        net_profit = total_sales - total_expenses
        avg_sale = total_sales / len(sales) if sales else 0
        
        stats_grid = GridLayout(cols=2, spacing=15, size_hint_y=0.4, padding=5)
        
        stats = [
            ('Gross Sales', f'${total_sales:.2f}', (0.3, 0.69, 0.31, 1)),
            ('Total Orders', str(len(sales)), (0.13, 0.59, 0.95, 1)),
            ('Net Profit', f'${net_profit:.2f}', (1, 0.6, 0, 1)),
            ('Avg Order', f'${avg_sale:.2f}', (0.61, 0.15, 0.69, 1))
        ]
        
        for title, value, color in stats:
            card = BoxLayout(orientation='vertical', padding=15, spacing=5)
            
            with card.canvas.before:
                Color(1, 1, 1, 1)
                card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
            card.bind(pos=lambda *args, c=card: setattr(c.rect, 'pos', c.pos))
            card.bind(size=lambda *args, c=card: setattr(c.rect, 'size', c.size))
            
            card.add_widget(Label(text=title, color=(0.5, 0.5, 0.5, 1), font_size='14sp'))
            card.add_widget(Label(text=f'[b]{value}[/b]', markup=True,
                                 font_size='26sp', color=color))
            stats_grid.add_widget(card)
        
        layout.add_widget(stats_grid)
        
        # Recent Sales
        layout.add_widget(Label(text='[b]Recent Sales[/b]', markup=True,
                               font_size='20sp', size_hint_y=0.08, 
                               color=(0.2, 0.2, 0.2, 1)))
        
        scroll = ScrollView(size_hint_y=0.42)
        content = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=5)
        content.bind(minimum_height=content.setter('height'))
        
        if not sales:
            content.add_widget(Label(text='No sales yet', color=(0.6, 0.6, 0.6, 1),
                                    font_size='16sp', size_hint_y=None, height=80))
        else:
            for sale in sales[:10]:
                item = BoxLayout(size_hint_y=None, height=60, padding=12, spacing=10)
                
                with item.canvas.before:
                    Color(0.97, 0.97, 0.97, 1)
                    item.rect = RoundedRectangle(pos=item.pos, size=item.size, radius=[8])
                item.bind(pos=lambda *args, i=item: setattr(i.rect, 'pos', i.pos))
                item.bind(size=lambda *args, i=item: setattr(i.rect, 'size', i.size))
                
                ref = str(sale.get('reference', 'N/A'))
                date = str(sale.get('date', ''))
                amt = float(sale.get('amount', 0))
                
                info = Label(text=f'[b]{ref}[/b]\n{date}', markup=True,
                            color=(0.2, 0.2, 0.2, 1), font_size='13sp',
                            halign='left', valign='middle')
                info.bind(size=info.setter('text_size'))
                
                amt_label = Label(text=f'[b]${amt:.2f}[/b]', markup=True,
                                 color=(0.3, 0.69, 0.31, 1), size_hint_x=0.3,
                                 font_size='16sp')
                
                item.add_widget(info)
                item.add_widget(amt_label)
                content.add_widget(item)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)


class JetstarPOSApp(App):
    def build(self):
        self.title = 'JETSTAR POS - Mobile'
        Window.size = (800, 600)  # Good for desktop testing
        
        self.db = Database()
        
        sm = ScreenManager()
        sm.add_widget(DashboardScreen(self.db, name='dashboard'))
        sm.add_widget(SellScreen(self.db, name='sell'))
        sm.add_widget(StockScreen(self.db, name='stock'))
        sm.add_widget(ExpensesScreen(self.db, name='expenses'))
        sm.add_widget(ReportsScreen(self.db, name='reports'))
        
        return sm


if __name__ == '__main__':
    JetstarPOSApp().run()
