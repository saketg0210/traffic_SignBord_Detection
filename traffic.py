from flask import *
import os
from werkzeug.utils import secure_filename
from keras.models import load_model
import numpy as np
from PIL import Image
import pyttsx3
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask import flash,redirect,url_for
import re
import smtplib

app = Flask(__name__) #Initialize the flask App
app.secret_key = 'your secret key'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'tiger'
app.config['MYSQL_DB'] = 'traffic'
 
mysql = MySQL(app)

classes = {0:'speed limit (20km/h)',
                1:'Speed limit (30km/h)',
                2:'Speed limit (50km/h)',
                3:'Speed limit (60km/h)',
                4:'Speed limit (70km/h)',
                5:'Speed limit (80km/h)',
                6:'End of speed limit (80km/h)',
                7:'Speed limit (100km/h)',
                8:'Speed limit (120km/h)',
                9:'No passing',
                10:'No passing veh over 3.5 tons',
                11:'Right-of-way at intersection',
                12:'Priority road',
                13:'Yield',
                14:'Stop',
                15:'No vehicles',
                16:'Vehicle > 3.5 tons prohibited',
                17:'No entry',
                18:'General caution',
                19:'Dangerous curve left',
                20:'Dangerous curve right',
                21:'Double curve',
                22:'Bumpy road',
                23:'Slippery road',
                24:'Road narrows on the right',
                25:'Road work',
                26:'Traffic signals',
                27:'Pedestrians',
                28:'Children crossing',
                29:'Bicycles crossing',
                30:'Beware of ice/snow',
                31:'Wild animals crossing',
                32:'End speed + passing limits!',
                33:'Turn right ahead',
                34:'Turn left ahead',
                35:'Ahead only',
                36:'Go straight or right',
                37:'Go straight or left',
                38:'Keep right',
                39:'Keep left',
                40:'Roundabout mandatory',
                41:'End of no passing',
                42:'End no passing vehicle > 3.5 tons',
                43:'No Sign Detected'
        }

def image_processing(img):
        model = load_model('./model/traffic.h5')
        data=[]
        image = Image.open(img)
        image = image.resize((30,30))
        data.append(np.array(image))
        X_test=np.array(data)
        Y_pred = model.predict_classes(X_test)
        return Y_pred

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/base')
def base():
    return render_template('base.html')
@app.route('/chart')
def chart():
    return render_template('chart.html')
@app.route('/first', methods=['GET'])
def first():
    return render_template('first.html')
@app.route('/performance')
def performance():
    return render_template('performance.html')
@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        file_path = secure_filename(f.filename)
        f.save(file_path)
        result = image_processing(file_path)
        s = [str(i) for i in result]
        a = int("".join(s))
        result = "Predicted Traffic Sign is: " +classes[a]
        engineio = pyttsx3.init()
        engineio.say(result)
        results=engineio.runAndWait()
        return result
        return results
    return None
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/loginaction', methods =['GET', 'POST'])
def loginaction():
    
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['pwd']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM register WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            return render_template('first.html')
        else:
            return render_template('login.html')

# @app.route('/preview', methods=['POST'])
# def preview():
#     if request.method == 'POST':
#         dataset = request.files['datasetfile']
#         df = pd.read_csv(dataset,encoding='unicode_escape')
#         return render_template("preview.html",df_view = df)

@app.route('/forgot')
def forgot():
    return render_template('forgot.html')


@app.route('/mail', methods=['POST'])
def mail():
    if request.method == 'POST':
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT password FROM register WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            smtp_username = '20d3071@science.claretcollege.edu.in'
            smtp_password = 'stpveypexxhvtsup'

            subject = 'Forgot Password'
            body = 'Your password is: ' + account['password']
            message = f'Subject: {subject}\n\n{body}'

            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(smtp_username, email, message)
                server.quit()

                flash('Mail sent successfully ,Go to login page', 'success')
            except Exception as e:
                print('Failed to send password:', e)
                flash('Failed to send mail', 'error')
        else:
            flash('Email not found', 'error')

    return redirect(url_for('forgot'))

# @app.route('/mail', methods=['POST'])
# def mail():
#     if request.method == 'POST':
#         email = request.form['email']
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT password FROM register WHERE email = %s', (email,))
#         account = cursor.fetchone()
#         #password = account[0]
#         #print("Password is", password)
#         if account:
#             smtp_server = 'smtp.gmail.com'
#             smtp_port = 587
#             smtp_username = '20d3071@science.claretcollege.edu.in'
#             smtp_password = 'stpveypexxhvtsup'

#             subject = 'Forgot Password'
#             body = 'Your password is:' + account['password']
#             message = f'Subject: {subject}\n\n{body}'
#             try:
#                 server = smtplib.SMTP(smtp_server, smtp_port)
#                 server.starttls()
#                 server.login(smtp_username, smtp_password)
#                 server.sendmail(smtp_username,email,message)
#                 server.quit()
#                 flash('Password sent successfully', 'success')
#             except Exception as e:
#                  print('Failed to send password:', e)
#                  flash('Failed to send password', 'error')
#     return render_template('login.html')

@app.route('/register',methods= ['GET',"POST"])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        username = request.form['uname']
        password = request.form['pwd']
        email = request.form['email']
        phone = request.form['pno']
        
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,10}$"
        pattern = re.compile(reg)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Check if account exists using MySQL)
        cursor.execute('SELECT * FROM register WHERE Username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not re.search(pattern,password):
            msg = 'Password should contain atleast one number, one lower case character, one uppercase character,one special symbol and must be between 6 to 10 characters long'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into employee table
            cursor.execute('INSERT INTO register VALUES (NULL, %s, %s, %s, %s)', (username, password, email, phone))
            mysql.connection.commit()
            flash('You have successfully registered! Please proceed for login!')
            return redirect(url_for('login'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        return msg
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)




if __name__ == '__main__':
    app.run(debug=True)