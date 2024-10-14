from datetime import datetime
import random
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import pyodbc
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'G:\Python\Flash Rest API\Shiv\Demo\Tour guides assign management\static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = b'8e21e1786c07fbc9e9b49c905d1bca5c39b7f4a2567c1361'
# Establish connection to the SQL Server database
conn = pyodbc.connect("Driver={SQL Server};SERVER=DESKTOP-F8GEPP7;Database=Guide;")
print("DB CONNECTED" ,conn)

# Create a cursor object
mysql2 = conn.cursor()
cursor = conn.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Home')
def Home():
    return render_template('index.html')

@app.route('/sign')
def sign():
    return render_template('sign_up.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Retrieve data from the form
        fast_name = request.form['fast']
        last_name = request.form['last']
        email_id = request.form['email']
        contact = request.form['contact']
        password = request.form['paaswd']  # contact Corrected misspelling of "password"

        insert_query = "INSERT INTO [Guide].[dbo].[User_Details]([fast_name],[last_name],[email_id],[contact],[password]) VALUES(?,?,?,?,?)"
        cursor.execute(insert_query,(fast_name,last_name,email_id,contact,password))
        conn.commit()
        return redirect(url_for('Home'))
        # return redirect(url_for('book'))
    else:
        return 'Invalid request method'
        # return redirect(url_for('book'))

@app.route('/rough')
def rough():
    email = session.get('email')
    return render_template('rough.html', email=email)

@app.route('/profile')
def profile():
    U_email = session.get('email')

    select_profile_query = "SELECT * FROM [Guide].[dbo].[User_Details] WHERE [email_id] = ?"
    cursor.execute(select_profile_query, U_email)
    profile_data = cursor.fetchall()

    select_show_records = "SELECT * FROM [Guide].[dbo].[Book_Details] WHERE [email_id] = ?"
    cursor.execute(select_show_records, U_email)
    booking_data = cursor.fetchall()

    return render_template('profile.html', profile_data=profile_data, booking_data=booking_data)

@app.route('/logout')
def logout():
    return redirect(url_for('Home'))

# @app.route('/show', methods=['GET', 'POST'])
# def show():
#     U_email = session.get('email')
#     select_show_records = "SELECT * FROM [Guide].[dbo].[Book_Details] WHERE [email_id] = ?"
#     cursor.execute(select_show_records,U_email)
#     data = cursor.fetchall()
#     return render_template('profile.html', data1=data)
@app.route('/guide')
def guide():
    select_query = "SELECT * FROM [Guide].[dbo].[Guide_Details]"
    cursor.execute(select_query)
    result = cursor.fetchall()
    print(result)
    return render_template('Guide.html',data=result)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search']
        select_query_search = "SELECT * FROM [Guide].[dbo].[Guide_Details] WHERE GID = ?"
        cursor.execute(select_query_search,search_query)
        result1 = cursor.fetchall()
        print(result1)
    return render_template('Guide.html',data=result1)

@app.route('/back', methods=['GET', 'POST'])
def back():
    return redirect(url_for('rough'))

@app.route('/book', methods=['GET', 'POST'])
def book():
    return render_template('book.html')

@app.route('/book_guide', methods=['GET', 'POST'])
def book_guide():
    if request.method == 'POST':
        # Get form data
        native_place = request.form['native_place']
        visiting_place = request.form['visiting_place']
        no_of_person = request.form['no_of_person']
        starting_date = request.form['starting_date']
        ending_date = request.form['ending_date']
        
        U_email = session.get('email')

        # Convert the date strings to datetime objects
        starting_date_dt = datetime.strptime(starting_date, '%Y-%m-%d')
        ending_date_dt = datetime.strptime(ending_date, '%Y-%m-%d')

        # Calculate the time difference in days
        time_difference = (ending_date_dt - starting_date_dt).days

        # If you want to get the absolute difference (ignoring the direction), use abs() function
        absolute_time_difference = abs(time_difference)

        total_time = absolute_time_difference * 24

        select_query = "SELECT * FROM [Guide].[dbo].[User_Details] WHERE [email_id] = ?"
        cursor.execute(select_query, U_email)
        user_result = cursor.fetchone()
        
        if user_result:
            select_guide_add_query = "SELECT [GID] FROM [Guide].[dbo].[Guide_Details]"
            cursor.execute(select_guide_add_query)
            guide_result = cursor.fetchall()

            # Check if there are any results
            if guide_result:
                # Choose a random index within the range of the result set
                random_index = random.randint(0, len(guide_result) - 1)

                # Fetch the GID from the tuple at the random_index
                random_gid = guide_result[random_index][0]

                select_guide_add_query = "SELECT [G_HourRate] FROM [Guide].[dbo].[Guide_Details] WHERE [GID] = ?"
                cursor.execute(select_guide_add_query, random_gid)
                guide_result = cursor.fetchall()
                print(guide_result[0][0])
                total_price = int(guide_result[0][0]) * total_time

                # Insert booking details into Book_Details table
                insert_book_query = "INSERT INTO [Guide].[dbo].[Book_Details]([fast_name],[last_name],[email_id],[contact],[N_place],[V_place],[N_person],[S_date],[E_date],[T_price],[GID]) VALUES(?,?,?,?,?,?,?,?,?,?,?)"
                cursor.execute(insert_book_query, (user_result[0], user_result[1], user_result[2], user_result[3], native_place, visiting_place, no_of_person, starting_date, ending_date, str(total_price), random_gid))
                conn.commit()

                return redirect(url_for('book'))
            else:
                return 'No guides available.'
        else:
            return 'User not found.'

    else:
        return 'Invalid request method'

    # return render_template('book.html')


# Route for displaying the login form
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email1 = request.form['email1']
        passwd1 = request.form['passwd1']
        # Check if the user exists in the database
    session['email'] = email1

    select_login_query = "SELECT * FROM [Guide].[dbo].[User_Details] WHERE [email_id] = ? AND [password] = ?"
    cursor.execute(select_login_query, email1, passwd1)
    result = cursor.fetchone()

    if result:
        return redirect(url_for('login_success'))
    else:
        if email1 == 'admin' and passwd1 == 'admin':
            return redirect(url_for('admin'))
        else:
            return 'Invalid to do the login'

# Route for displaying login success page
@app.route('/login/success')
def login_success():
    return redirect(url_for('rough'))


# Flask routes
@app.route('/admin')
def admin():
    select_query = "SELECT * FROM [Guide].[dbo].[Guide_Details]"
    cursor.execute(select_query)
    result = cursor.fetchall()
    print(result)

    select_show_records = "SELECT * FROM [Guide].[dbo].[Book_Details]"
    cursor.execute(select_show_records)
    booking_data = cursor.fetchall()

    select_user_records = "SELECT * FROM [Guide].[dbo].[User_Details]"
    cursor.execute(select_user_records)
    user_data = cursor.fetchall()

    select_feedback_records = "SELECT * FROM [Guide].[dbo].[Feedback_Details]"
    cursor.execute(select_feedback_records)
    feedback_data = cursor.fetchall()

    # return render_template('Guide.html',data=result)
    return render_template('admin.html',data=result,booking_data=booking_data,user_data=user_data,feedback_data=feedback_data)

@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        # Retrieve form data
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                filename = secure_filename(image.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
        gid = request.form['gid']
        guide_name = request.form['guideName']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        adhar = request.form['adhar']
        language = request.form.getlist('language')  # Use getlist to get multiple values from checkboxes
        per_hour = request.form['perHour']
        available_areas = request.form['availableAreas']

        # Insert data into SQL Server database
        insert_query = "INSERT INTO [dbo].[Guide_Details] ([G_Image], [GID], [G_Name], [G_Email], [G_Phone], [G_Address], [G_Adhar], [G_Language], [G_HourRate], [G_Area]) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(insert_query, image.filename, gid, guide_name, email, phone, address, adhar, ','.join(language), per_hour, available_areas)
        conn.commit()

        return 'Guide added successfully!'
    else:
        return 'Guide not added successfully!'

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        insert_feedback_query = "INSERT INTO [Guide].[dbo].[Feedback_Details]([F_Name],[F_Email],[F_Message]) VALUES(?,?,?)"
        cursor.execute(insert_feedback_query, name, email, message)
        conn.commit()

        return redirect(url_for('Home'))
        
    else:
        return 'Feedback not added successfully!'


if __name__ == '__main__':
    app.run(debug=True)