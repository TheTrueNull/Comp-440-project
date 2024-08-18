#Comp 488- Phase 2
#by: Edward Orlov, Rucha Kothikar, Pragya Sangwan
#3 python libraries are required to run the app, run the following commands before executing the code:
#pip install flask 
#pip install mysql-connector-python 
#pip install bcrypt 

from datetime import date
from flask import Flask, request, render_template, redirect, render_template_string, make_response
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
            response = make_response(redirect('/dashboard'))
            response.set_cookie('username', username)
            return response
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

@app.route('/dashboard')
def dashboard():
    return render_template('userdash.html')

@app.route('/logout', methods=['GET']) 
def logout():
    response = make_response(redirect('/'))
    response.set_cookie('username', '', expires=0)
    return response

        
@app.route('/insert_item', methods=['POST'])
def insert_item():
    title = request.form['title']
    description = request.form['description']
    categories = request.form['categories']
    price = request.form['price']
    username = request.cookies.get('username')  # Ensure the username is being fetched correctly.
    today = date.today()

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Items WHERE username = %s AND datePosted = %s", (username, today))
    item_count = cursor.fetchone()[0]
    
    if item_count >= 2:
        return render_template('userdash.html', item_error="Limit reached: You can only post 2 items per day.")
    
    try:
        cursor.execute("INSERT INTO Items (username, title, description, categories, price, datePosted) VALUES (%s, %s, %s, %s, %s, %s)", 
                       (username, title, description, categories, price, today))
        conn.commit()
        return redirect('/dashboard?success=True')
    except Error as e:
        print(e)
        return render_template('userdash.html', item_error=str(e))
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

@app.route('/all_items', methods=['GET'])
def all_items():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Items")
    items = cursor.fetchall()
    return render_template('query_results.html', items=items)

@app.route('/all_reviews', methods=['GET'])
def all_reviews():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT r.reviewID, r.itemID, t.username, r.username, r.reviewDate, r.score, r.remark, t.title, t.categories FROM Reviews r, Items t where r.itemID = t.itemID")
    reviews = cursor.fetchall()
    return render_template('query_results.html', reviews=reviews)

@app.route('/query1', methods=['GET'])
def query1():
    conn = db_connection()
    cursor = conn.cursor()
    # cursor.execute("SELECT categories, MAX(price) AS MaxPrice, title, description FROM Items GROUP BY categories") 
    # some strange issue with group by in this query: running this line in mysql fixes it SET SESSION sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY','')); 
    cursor.execute("""SELECT i.*, m.MaxPrice
    FROM Items i
    JOIN (SELECT categories, MAX(price) AS MaxPrice 
    FROM Items
    GROUP BY categories) m ON i.categories = m.categories AND i.price = m.MaxPrice;""") #this workaround seems to work but was much more difficult to implement and may cause unforeseen issues
    items = cursor.fetchall()
    return render_template('query_results.html', items=items)

@app.route('/query2', methods=['GET'])
def query2():
    categoryX = request.args.get('categoryX')
    categoryY = request.args.get('categoryY')
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT i1.username
        FROM Items i1, Items i2
        WHERE i1.username = i2.username 
        AND i1.datePosted = i2.datePosted
        AND i1.categories = %s
        AND i2.categories = %s
        AND i1.itemID != i2.itemID
    """, (categoryX, categoryY))
    users = cursor.fetchall()
    return render_template('query_results.html', users=users)

@app.route('/query3', methods=['GET'])
def query3():
    username = request.args.get('username')
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT DISTINCT i.*
    FROM Items i
    JOIN Reviews r ON i.itemID = r.itemID
    WHERE i.username = %s
    AND NOT EXISTS (
    SELECT 1
    FROM Reviews r2
    WHERE r2.itemID = i.itemID
    AND r2.score NOT IN ('Excellent', 'Good')
);
    """, (username,))
    items = cursor.fetchall()
    return render_template('query_results.html', items=items)

@app.route('/query4', methods=['GET'])
def query4():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, COUNT(*) AS Countno
        FROM Items
        WHERE datePosted = '2024-07-04'
        GROUP BY username
        HAVING COUNT(*) = (
            SELECT MAX(Countno) FROM (
                SELECT COUNT(*) AS Countno
                FROM Items
                WHERE datePosted = '2024-07-04'
                GROUP BY username
            ) AS Counts
        )
    """)
    users = cursor.fetchall()
    return render_template('query_results.html', users=users)

@app.route('/query5', methods=['GET'])
def query5():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT DISTINCT i.username
    FROM Items i
    JOIN Reviews r ON i.itemID = r.itemID
    GROUP BY i.username
    HAVING COUNT(*) = COUNT(CASE WHEN r.score = 'Poor' THEN 1 END);
    """)
    users = cursor.fetchall()
    return render_template('query_results.html', users=users)

@app.route('/query6', methods=['GET'])
def query6():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""
     SELECT DISTINCT i.username
    FROM Items i
    WHERE i.username NOT IN (
    SELECT r.username
    FROM Reviews r
    JOIN Items it ON r.itemID = it.itemID
    WHERE r.score = 'Poor'
);
    """)
    users = cursor.fetchall()
    return render_template('query_results.html', users=users)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    itemID = request.form['itemID']
    score = request.form['score']
    remark = request.form['remark']
    username = request.cookies.get('username')
    today = date.today()

    conn = db_connection()
    cursor = conn.cursor()

    # Check ownership
    cursor.execute("SELECT username FROM Items WHERE itemID = %s", (itemID,))
    owner = cursor.fetchone()
    if owner and owner[0] == username:
        return render_template('userdash.html', review_error="You cannot review your own items.")

    # Check daily limit
    cursor.execute("SELECT COUNT(*) FROM Reviews WHERE username = %s AND reviewDate = %s", (username, today))
    count = cursor.fetchone()[0]
    if count >= 3:
        return render_template('userdash.html', review_error="Limit reached: You can only submit 3 reviews per day.")

    # Check previous review
    cursor.execute("SELECT * FROM Reviews WHERE itemID = %s AND username = %s", (itemID, username))
    if cursor.fetchone():
        return render_template('userdash.html', review_error="You have already reviewed this item.")

    try:
        cursor.execute("INSERT INTO Reviews (itemID, username, score, remark, reviewDate) VALUES (%s, %s, %s, %s, %s)",
                       (itemID, username, score, remark, today))
        conn.commit()
        return redirect('/dashboard?review_success=True')
    except Error as e:
        print(e)
        return render_template('userdash.html', review_error="Error occurred during the review process.")
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
