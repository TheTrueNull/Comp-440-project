It is very important that you have python installed along with the following 3 libraries:
pip install flask 
pip install mysql-connector-python 
pip install bcrypt 

It is also important to create a new Database and use the "Database creation queries.sql" script file to generate the required tables, 
then after creating the schema you have to add a new user using administration tools in the mysql workbench and make sure to only give it Insert and Select privalages for security purposes.

Then make sure to use the newly created user information at the top of the server.py file, which should look something like this:

 conn = mysql.connector.connect(
            host='localhost',        
            database='comp440db',
            user='devuser', #REPLACE THIS WITH YOUR NEWLY CREATED USERS INFORMATION
            password='liability' #REPLACE THIS WITH YOUR NEWLY CREATED USERS INFORMATION
        )
PHASE 1 DEMO: https://www.youtube.com/watch?v=9c8RjTPLesw

PHASE 2 DEMO: https://www.youtube.com/watch?v=AzV-NQbLbBk