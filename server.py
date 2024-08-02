#Comp 488- Phase 1
#by: Edward Orlov, Rucha Kothikar, Pragya Sangwan
#3 python libraries are required to run the app, run the following commands before executing the code:
#pip install flask 
#pip install mysql-connector-python 
#pip install bcrypt 

from datetime import date
from flask import Flask, request, render_template, redirect, render_template_string
import mysql.connector
from mysql.connector import Error
import bcrypt

app = Flask(__name__)

def db_connection():
    conn = None
    try:
        conn = mysql.connector.connect(
            host='localhost',        
            database='comp440db',
            user='devuser', #REPLACE THIS WITH YOUR NEWLY CREATED USERS INFORMATION
            password='liability' #REPLACE THIS WITH YOUR NEWLY CREATED USERS INFORMATION
        )
    except Error as e:
        print(e)
    return conn

# Default route for sign-in
@app.route('/', methods=['GET'])
def home():
      # passing an empty error message initially
    return render_template('signin.html', error='')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = db_connection()
    cursor = conn.cursor(prepared=True)
    try:
        cursor.execute('SELECT password FROM Users WHERE username = %s', (username,))
        record = cursor.fetchone()
        if record and bcrypt.checkpw(password.encode(), record[0].encode()):
            return render_template('userdash.html')
        else:
            error = "Incorrect login, please check your login info and try again!"
            return render_template('signin.html', error=error)
    except Error as e:
        print(e)
        error = "Error occurred during login"
        return render_template('signin.html', error=error)
    finally:
        cursor.close()
        conn.close()

# Route for user registration
@app.route('/register', methods=['GET'])
def register():
    return render_template('registration.html')

# Route to handle the form submission
@app.route('/register_user', methods=['POST'])
def register_user():
    username = request.form['username']
    password = request.form['password']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['email']

    # Additional password confirmation handling
    confirm_password = request.form['confirm_password']
    if password != confirm_password:
        return render_template('registration.html', error="Passwords do not match.")

    valid, message = validate_input(username, password, email)
    if not valid:
        return render_template('registration.html', error=message)

    hashed_password = hash_password(password)

    conn = db_connection()
    cursor = conn.cursor(prepared=True)
    try:
        cursor.execute('''
            INSERT INTO Users (username, password, firstName, lastName, email)
            VALUES (%s, %s, %s, %s, %s)
        ''', (username, hashed_password, firstName, lastName, email))
        conn.commit()
        # HTML response with a button to return to the login page
        return render_template_string('''
            User registered successfully! <br>
            <button onclick="window.location.href='/'">Return to Login</button>
        ''')
    except Error as e:
        print(e)
        return render_template('registration.html', error='Error occurred during registration.')
    finally:
        cursor.close()
        conn.close()
@app.route('/insert_item', methods=['POST'])
def insert_item():
    title = request.form['title']
    description = request.form['description']
    categories = request.form['categories']
    price = request.form['price']
    username = request.cookies.get('username')  # Assuming username is stored in cookies
    today = date.today()

    conn = db_connection()
    cursor = conn.cursor()
    # Check the number of items posted today
    cursor.execute("SELECT COUNT(*) FROM Items WHERE username = %s AND datePosted = %s", (username, today))
    count = cursor.fetchone()[0]
    if count >= 2:
        return "Limit reached: You can only post 2 items per day."

    try:
        cursor.execute("INSERT INTO Items (title, description, categories, price, username, datePosted) VALUES (%s, %s, %s, %s, %s, %s)",
                       (title, description, categories, float(price), username, today))
        conn.commit()
        return "Item inserted successfully!"
    except Error as e:
        print(e)
        return "Error occurred"
    finally:
        cursor.close()
        conn.close()

@app.route('/search_items', methods=['GET'])
def search_items():
    category = request.args.get('category')
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Items WHERE categories LIKE %s", ('%' + category + '%',))
    items = cursor.fetchall()
    return render_template('items.html', items=items)  # Assuming you have an items.html to display results

@app.route('/submit_review', methods=['POST'])
def submit_review():
    itemID = request.form['itemID']
    score = request.form['score']
    remark = request.form['remark']
    username = request.cookies.get('username')  # Assuming username is stored in cookies
    today = date.today()

    conn = db_connection()
    cursor = conn.cursor()

    # Check if the user owns the item
    cursor.execute("SELECT username FROM Items WHERE itemID = %s", (itemID,))
    owner = cursor.fetchone()
    if owner[0] == username:
        return "You cannot review your own items."

    # Check the number of reviews today
    cursor.execute("SELECT COUNT(*) FROM Reviews WHERE username = %s AND reviewDate = %s", (username, today))
    count = cursor.fetchone()[0]
    if count >= 3:
        return "Limit reached: You can only submit 3 reviews per day."

    # Check if the user has already reviewed this item
    cursor.execute("SELECT * FROM Reviews WHERE itemID = %s AND username = %s", (itemID, username))
    if cursor.fetchone():
        return "You have already reviewed this item."

    try:
        cursor.execute("INSERT INTO Reviews (itemID, username, score, remark, reviewDate) VALUES (%s, %s, %s, %s, %s)",
                       (itemID, username, score, remark, today))
        conn.commit()
        return "Review submitted successfully!"
    except Error as e:
        print(e)
        return "Error occurred"
    finally:
        cursor.close()
        conn.close()

#function to validate user input
def validate_input(username, password, email):
    if not username.isalnum() or not 5 <= len(username) <= 20:
        return False, "Username must be 5-20 characters long and alphanumeric."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if '@' not in email:
        return False, "Invalid email format."
    return True, ""

#function for hashing password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

if __name__ == '__main__':
    app.run(debug=True)
