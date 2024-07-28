#Comp 488- Phase 1
#by: Edward Orlov, Pragya,
#4 python libraries which are needed to install, run the following commands before executing the code:
#pip install flask 
#pip install mysql-connector-python 
#pip install bcrypt 

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
            user='devuser', #this user only has insert and select permissions
            password='liability'
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
            return 'Login successful!'
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
