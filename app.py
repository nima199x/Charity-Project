from flask import Flask, render_template, request
import sqlite3
from abc import ABC, abstractmethod

app = Flask(__name__)

# 1. Creational Patterns

# Singleton Pattern for Database
class DatabaseSingleton:
    _instance = None

    @staticmethod
    def get_instance():
        if DatabaseSingleton._instance is None:
            DatabaseSingleton._instance = SQLiteDatabase('charity.sqlite')
        return DatabaseSingleton._instance

class DatabaseInterface(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def create_donation_table(self):
        pass

    @abstractmethod
    def insert_donation(self, name, amount, project_name=None, notes=None):
        pass

    @abstractmethod
    def fetch_donations(self):
        pass

class SQLiteDatabase(DatabaseInterface):
    def __init__(self, db_name):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_donation_table(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS donation (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            amount REAL NOT NULL,
                            date TEXT DEFAULT CURRENT_TIMESTAMP,
                            project_name TEXT,
                            notes TEXT)''')
        conn.commit()
        conn.close()

    def insert_donation(self, name, amount, project_name=None, notes=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO donation (name, amount, project_name, notes) VALUES (?, ?, ?, ?)''',
                       (name, amount, project_name, notes))
        conn.commit()
        conn.close()

    def fetch_donations(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM donation;')
        donations = cursor.fetchall()
        conn.close()
        return donations

# 2. Factory Method Pattern
class DonationFactory:
    @staticmethod
    def create_donation(name, amount, project_name=None, notes=None):
        return {
            'name': name,
            'amount': amount,
            'project_name': project_name,
            'notes': notes
        }

# 3. Facade Pattern
class DonationFacade:
    def __init__(self, db: DatabaseInterface):
        self.db = db
        self.db.create_donation_table()

    def donate(self, name, amount, project_name=None, notes=None):
        donation = DonationFactory.create_donation(name, amount, project_name, notes)
        self.db.insert_donation(**donation)

    def view_donations(self):
        return self.db.fetch_donations()

# 4. Proxy Pattern
class DonationProxy:
    def __init__(self, facade: DonationFacade):
        self.facade = facade

    def donate(self, name, amount, project_name=None, notes=None):
        print(f"Processing donation from {name}...")
        self.facade.donate(name, amount, project_name, notes)

    def view_donations(self):
        donations = self.facade.view_donations()
        for donation in donations:
            print(donation)
        return donations

# 5. Observer Pattern (simplified)
class DonationObserver:
    def notify(self, donation):
        print(f"New donation received: {donation}")

# Initialize database and facade
db = DatabaseSingleton.get_instance()
donation_facade = DonationFacade(db)
donation_proxy = DonationProxy(donation_facade)
observer = DonationObserver()

@app.route('/')
def home():
    return render_template('donation_form.html')

@app.route('/donate', methods=['POST'])
def donate():
    name = request.form['name']
    amount = request.form['amount']
    project_name = request.form.get('project_name', None)
    notes = request.form.get('notes', None)

    donation_proxy.donate(name, amount, project_name, notes)

    # Notify observer
    observer.notify({'name': name, 'amount': amount, 'project_name': project_name, 'notes': notes})

    return f"متشکریم {name}، شما {amount} تومان کمک کردید!"

@app.route('/view_donations')
def view_donations():
    donations = donation_proxy.view_donations()
    return render_template('view_donations.html', donations=donations)

if __name__ == '__main__':
    app.run(debug=True)
