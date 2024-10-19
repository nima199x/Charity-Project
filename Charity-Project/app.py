from flask import Flask, render_template, request, redirect
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
    
    @abstractmethod
    def fetch_donation_by_id(self, donation_id):
        pass
    
    @abstractmethod
    def update_donation(self, donation_id, name, amount, project_name=None, notes=None):
        pass

    @abstractmethod
    def delete_donation(self, donation_id):
        pass

class SQLiteDatabase(DatabaseInterface):
    def __init__(self, db_name):
        self.db_name = db_name
        self.create_donation_table()  # Ensure table exists on initialization

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

    def fetch_donation_by_id(self, donation_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM donation WHERE id = ?;', (donation_id,))
        donation = cursor.fetchone()
        conn.close()
        return donation

    def update_donation(self, donation_id, name, amount, project_name=None, notes=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''UPDATE donation SET name = ?, amount = ?, project_name = ?, notes = ? WHERE id = ?''',
                       (name, amount, project_name, notes, donation_id))
        conn.commit()
        conn.close()

    def delete_donation(self, donation_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM donation WHERE id = ?;', (donation_id,))
        conn.commit()
        conn.close()

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

    def donate(self, name, amount, project_name=None, notes=None):
        donation = DonationFactory.create_donation(name, amount, project_name, notes)
        self.db.insert_donation(**donation)

    def view_donations(self):
        return self.db.fetch_donations()
    
    def edit_donation(self, donation_id):
        return self.db.fetch_donation_by_id(donation_id)

    def update_donation(self, donation_id, name, amount, project_name=None, notes=None):
        self.db.update_donation(donation_id, name, amount, project_name, notes)

    def delete_donation(self, donation_id):
        self.db.delete_donation(donation_id)

# 4. Proxy Pattern
class DonationProxy:
    def __init__(self, facade: DonationFacade):
        self.facade = facade

    def donate(self, name, amount, project_name=None, notes=None):
        print(f"Processing donation from {name}...")
        self.facade.donate(name, amount, project_name, notes)

    def view_donations(self):
        donations = self.facade.view_donations()
        return donations

# Initialize database and facade
db = DatabaseSingleton.get_instance()
donation_facade = DonationFacade(db)
donation_proxy = DonationProxy(donation_facade)

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

    return render_template('thank_you.html')

@app.route('/view_donations')
def view_donations():
    donations = donation_proxy.view_donations()
    return render_template('view_donations.html', donations=donations)

@app.route('/edit_donation/<int:id>', methods=['GET', 'POST'])
def edit_donation(id):
    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        project_name = request.form.get('project_name', None)
        notes = request.form.get('notes', None)
        donation_proxy.facade.update_donation(id, name, amount, project_name, notes)
        return redirect('/view_donations')

    donation = donation_proxy.facade.edit_donation(id)
    return render_template('edit_donation.html', donation=donation)

@app.route('/delete_donation/<int:id>')
def delete_donation(id):
    donation_proxy.facade.delete_donation(id)
    return redirect('/view_donations')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
