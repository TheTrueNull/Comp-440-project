from flask import Flask, request, render_template, redirect
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

def db_connection():
    conn = None
    try:
        conn = mysql.connector.connect(
            host='localhost',        # Working on the database connection currently
            database='comp440db',
            user='root',
            password='liability'
        )
    except Error as e:
        print(e)
    return conn

# Default route for sign-in
@app.route('/', methods=['GET'])
def home():
    return render_template('signin.html')

# Route to handle sign-in
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']  # Note: Password should be hashed

    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT password FROM Users WHERE username = %s', (username,))
        record = cursor.fetchone()
        if record and record[0] == password:
            return 'Login successful!'  # Redirect to another page or dashboard
        else:
            return 'Login failed! Invalid username or password.'
    except Error as e:
        print(e)
        return 'Error occurred during login'
    finally:
        cursor.close()
        conn.close()

# Route for user registration
@app.route('/register', methods=['GET'])
def register():
    return render_template('registration.html')

if __name__ == '__main__':
    app.run(debug=True)
