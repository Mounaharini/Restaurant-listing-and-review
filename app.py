from flask import Flask, render_template,request
import sqlite3
import os
import pandas as pd
import smtplib 
import threading
 
admin=False
login_user=False
username=None
resto_name=None
tableid=None

def connect_db():
    conn = sqlite3.connect('Database.db', check_same_thread=False)
    return conn 
def dataframe():
    conn=connect_db()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM Restaurants")
    results = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame(results, columns=columns)
    # Close the cursor and database connection
    cursor.close()
    return df
def mail(contact_name,reservation_date,reservation_time,num_guests,special_requests,to):
    global tableid
    ob=smtplib.SMTP("smtp.gmail.com",587)
    ob.starttls()
    ob.login("himanshumanral2003@gmail.com","qvicfgwfprwbnlrd")
    subject="Reservation Confirmed"
    body=f"Dear {contact_name},\n\nThank you for booking a table at our restaurant!\n\nHere are the details of your reservation:\n\nDate: {reservation_date}\nTime: {reservation_time}\nNumber of Guests: {num_guests}\nTable Id:{tableid}\nSpecial Requests: {special_requests}\n\nWe look forward to welcoming you!\n\nBest regards,\nYour Restaurant Team"
    mes="subject:{}\n\n{}".format(subject,body)
    print(mes)
    listofadd=[to]
    ob.sendmail("himanshumanral2003@gmail.com",listofadd,mes)
    ob.quit()
def notification_mail():
    global tableid
    ob=smtplib.SMTP("smtp.gmail.com",587)
    ob.starttls()
    ob.login("himanshumanral2003@gmail.com","qvicfgwfprwbnlrd")
    subject="New Restaurant Listed"
    body="Experience the culinary delights of our newly opened restaurant in the heart of the city and indulge in a gastronomic journey like no other. Discover exquisite flavors, impeccable service, and an inviting ambiance that will leave you craving for more. Come, be our guest, and savor the delectable creations crafted by our talented chefs. Your taste buds deserve this extraordinary experience!\n\nBest regards,\nYour Restaurant Team"
    mes="subject:{}\n\n{}".format(subject,body)
    conn=connect_db()
    cursor=conn.cursor()
    cursor.execute("SELECT email FROM login_details")
    listofadd = []
    for row in cursor.fetchall():
        listofadd.append(row[0])
    ob.sendmail("himanshumanral2003@gmail.com",listofadd,mes)
    ob.quit() 
def notification_thread():
    # Call the notification_mail() function here
    notification_mail()
thread = threading.Thread(target=notification_thread)           
    
app = Flask(__name__)

UPLOAD_FOLDER = 'static/restaurant'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    global admin,login_user,username
    if admin:
       return render_template('base.html',username=username)
    elif login_user:
        return render_template('login_user.html',username=username)
    else:
        return render_template('normal_user.html')
@app.route('/logout')
def logout():
    return render_template('normal_user.html')

@app.route('/discover')
def discover():
    global admin,login_user,username
    return render_template('discover.html',admin=admin,login_user=login_user,username=username)
@app.route('/login', methods=["GET","POST"])
def login():
    global admin,login_user,username
    if request.method=="POST":
        email=request.form['email']
        passw=request.form['password']
        conn=connect_db()
        cursor=conn.cursor()
        cursor.execute("SELECT username FROM login_details WHERE email = ? AND password = ?", (email, passw))
        record = cursor.fetchone() 
         
        if record:
            if passw=="admin@123":
                admin=True
                login_user=False
                username=record[0]
                return render_template('discover.html',admin=admin,username=username)
            else:
                login_user=True
                admin=False
                username=record[0]
                return render_template("login_user.html",username=username,login_user=login_user)
        else :
            return render_template('login.html',msg="Invalid Credentials")

    return render_template("login.html")
@app.route('/newuser', methods=["GET","POST"])
def newuser():
    global admin,login_user
    if request.method=="POST":
        print("reached")
        username=request.form['username'] 
        password=request.form['password']
        email=request.form['email']
        conn=connect_db()
        cursor=conn.cursor()
        # Inserting the values into the database
        cursor.execute("INSERT INTO login_details (username, password, email) VALUES (?, ?, ?)",
                       (username, password, email))
        
        conn.commit()
        return render_template("newuser.html",msg="Account Created Successfully !",admin=admin,login_user=login_user)
           
    return render_template("newuser.html",admin=admin,login_user=login_user)
@app.route("/details" , methods=['GET','POST'])
def new_retro():
    global admin,username
    if request.method=='POST':
        conn=connect_db()
        cursor=conn.cursor()
        restro_name=request.form['restaurantName']
        rating=request.form['rating']
        address=request.form['address']
        opening_hour=request.form['openingHour']
        closing_hour=request.form['closingHour']
        total_tables=request.form['totalTables']
        family_Tables=request.form['familyTables']
        two_person=request.form['twoPersonTables']
        outdoor_tables=request.form['outdoorTables']
        ph_no=request.form['phoneNo']
        file = request.files['image']
        image_path=os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)
        cursor.execute("INSERT INTO Restaurants (restaurant_name , rating, address, opening_time, closing_time, total_tables, family_tables, two_person_tables, outdoor_tables,phone_no,image) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (restro_name, rating, address, opening_hour, closing_hour, total_tables, family_Tables, two_person, outdoor_tables, ph_no,image_path))
        conn.commit() 
        thread.start()
        return render_template ("listing.html",msg="Resraurant Listed Succesfully !",admin=admin,username=username)
    return render_template ("listing.html",admin=admin,username=username)


@app.route('/images')
def get_images():
    global admin,login_user,username
    conn = connect_db()
    cursor = conn.cursor()
    # Retrieve all the image data from the database
    cursor.execute("SELECT image FROM Restaurants")
    results = cursor.fetchall()  
    images = []
    for result in results:
        images.append(result[0])
    df=dataframe() 
    restaurant_names = df['restaurant_name'].tolist()
    ratings = df['rating'].tolist()
    addresses = df['address'].tolist()
    opening_times = df['opening_time'].tolist()
    closing_times = df['closing_time'].tolist()
    available_tables=df['available_tables'].tolist()
    return render_template('restro_list.html', images=images, restaurant_names=restaurant_names, ratings=ratings, addresses=addresses, opening_times=opening_times, closing_times=closing_times,available_tables=available_tables,admin=admin,login_user=login_user,username=username)     


@app.route('/Dashboard')
def dashbord():
    global admin,username
    return render_template ("dashbord.html",admin=admin,username=username)

@app.route('/table/<string:restro_name>/', methods=['GET','POST'])
def Table(restro_name):
    global admin,login_user,username,resto_name
    conn=connect_db()
    cursor=conn.cursor()
    if request.method=='GET':
        resto_name=restro_name
        print(resto_name)
        return render_template ("table_book.html",name=resto_name,admin=admin,login_user=login_user,username=username)
     
        
    return render_template("table_book.html")
    
@app.route("/table/<string:restro_name>/confirm", methods=['GET', 'POST'])
def confirm(restro_name):
    global admin, login_user, username, resto_name
    if request.method == "POST":
        conn = connect_db()
        cursor = conn.cursor()
        reservation_date = request.form['reservationDate']
        reservation_time = request.form['reservationTime']
        num_guests = int(request.form['guests'])
        contact_name = request.form['contactName']
        contact_email = request.form['contactEmail']
        special_requests = request.form['specialRequests']
        cursor.execute("SELECT available_tables FROM Restaurants WHERE restaurant_name = ?", (restro_name,))
        result = cursor.fetchone()
        conn.commit()
        if result:
            available_tables = result[0]
            if available_tables > 0:
                mail(contact_name=contact_name, reservation_date=reservation_date, reservation_time=reservation_time, num_guests=num_guests, special_requests=special_requests,to=contact_email)
                cursor.execute("UPDATE Restaurants SET available_tables = ? WHERE restaurant_name = ?", (available_tables - 1, restro_name))
                conn.commit()
                return render_template("table_book.html", msg="Reservation Confirmed", admin=admin, login_user=login_user, username=username)
            else:
                return render_template("table_book.html", msg="Restaurant Full", admin=admin, login_user=login_user, username=username)
    return render_template("table_book.html", admin=admin, login_user=login_user, username=username)


@app.route("/top_5_by_rating", methods=['GET', 'POST'])
def top5():
    conn = connect_db()
    cursor = conn.cursor()

    rating_list = []

    # Execute the query to retrieve ratings
    cursor.execute("SELECT rating FROM Restaurants")

    # Fetch all the results as a list of tuples
    results = cursor.fetchall()

    # Append the ratings to the rating_list
    for result in results:
        rating_list.append(result[0])

    # Sort the rating_list in descending order
    rating_list.sort(reverse=True)

    # Close the database connection
    conn.close()

    # Get the top 5 ratings
    top_ratings = rating_list[:5]

    # Create an empty DataFrame
    df = pd.DataFrame(columns=["restaurant_name", "rating", "address", "opening_time", "closing_time", "available_tables", "image"])

    # Fetch rows based on top ratings
    conn = connect_db()
    cursor = conn.cursor()
    appended_restaurants = set()  # To keep track of already appended restaurants
    for rating in top_ratings:
        cursor.execute("SELECT restaurant_name, rating, address, opening_time, closing_time, available_tables, image FROM Restaurants WHERE rating = ?", (rating,))
        rows = cursor.fetchall()
        for row in rows:
            restaurant_name = row[0]
            if restaurant_name not in appended_restaurants:
                df = df.append({"restaurant_name": row[0], "rating": row[1], "address": row[2], "opening_time": row[3], "closing_time": row[4], "available_tables": row[5], "image": row[6]}, ignore_index=True)
                appended_restaurants.add(restaurant_name)

    # Close the database connection
    conn.close()

    # Fetch the required columns as lists
    restaurant_names = df['restaurant_name'].tolist()
    ratings = df['rating'].tolist()
    addresses = df['address'].tolist()
    opening_times = df['opening_time'].tolist()
    closing_times = df['closing_time'].tolist()
    available_tables = df['available_tables'].tolist()
    image = df['image'].tolist()

    return render_template("top_5_by_rating.html", restaurant_names=restaurant_names, ratings=ratings, addresses=addresses, opening_times=opening_times, closing_times=closing_times, available_tables=available_tables, image=image, admin=admin, login_user=login_user, username=username)


@app.route('/rate/<string:restro_name>/', methods=['GET', 'POST'])
def Rate(restro_name):
    global admin, login_user, username
    return render_template("Rating_form.html", name=restro_name, admin=admin, login_user=login_user, username=username)
@app.route('/rate/<string:restro_name>/send', methods=['GET', 'POST'])
def send_rate(restro_name):
        global admin, login_user, username
        conn = connect_db()
        cursor = conn.cursor()

        if request.method == 'POST':
            name = request.form['name']
            rating =int(request.form['rating'])
            review = request.form['review']

            # Execute the query to insert values into the Rating table
            cursor.execute("INSERT INTO Rating (Name, Rating, Review,restaurant_name) VALUES(?, ?, ?, ?)",
                        (name, rating, review,restro_name))
            conn.commit()

            return render_template("Rating_form.html",msg="Thanks For your Feedback!",name=restro_name, admin=admin, login_user=login_user,
                                username=username)    
        return render_template("Rating_form.html", name=restro_name, admin=admin, login_user=login_user, username=username)


@app.route("/ratings/<string:restro_name>/", methods=['GET', 'POST'])
def ratings(restro_name):
    global admin, login_user, username
    conn = connect_db()
    cursor = conn.cursor()
    
    # Execute the query to retrieve ratings for the given restaurant name
    cursor.execute("SELECT restaurant_name,name,rating, review FROM Rating WHERE restaurant_name=?", (restro_name,))
    
    # Fetch all the results as a list of tuples
    results = cursor.fetchall()
    
    # Create a DataFrame from the results
    df = pd.DataFrame(results, columns=['restaurant_name','name','rating', 'review'])
    
    # Close the database connection
    conn.close()
    
    # Convert each column of the DataFrame into a separate list
    restaurant_names = df['restaurant_name'].tolist()
    name_of_user=df['name'].tolist()
    ratings = df['rating'].tolist()
    reviews = df['review'].tolist()
    
    return render_template("ratings.html", admin=admin, login_user=login_user, username=username, restro_name=restro_name, restaurant_names=restaurant_names, ratings=ratings,name_of_user=name_of_user, reviews=reviews)
@app.route("/delete/<string:restro_name>/", methods=['GET', 'POST'])
def delete(restro_name):
    global admin,login_user,username
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Restaurants WHERE restaurant_name =?",(restro_name,))
    conn.commit()
    return render_template('dashbord.html',admin=admin,login_user=login_user,username=username)
@app.route("/manage_restro")
def manage_restro():
    global admin,login_user,username
    conn = connect_db()
    cursor = conn.cursor()
    # Retrieve all the image data from the database
    cursor.execute("SELECT image FROM Restaurants")
    results = cursor.fetchall()  
    images = []
    for result in results:
        images.append(result[0])
    df=dataframe() 
    restaurant_names = df['restaurant_name'].tolist()
    ratings = df['rating'].tolist()
    addresses = df['address'].tolist()
    opening_times = df['opening_time'].tolist()
    closing_times = df['closing_time'].tolist()
    available_tables=df['available_tables'].tolist()
    return render_template('manage_restro.html', images=images, restaurant_names=restaurant_names, ratings=ratings, addresses=addresses, opening_times=opening_times, closing_times=closing_times,available_tables=available_tables,admin=admin,login_user=login_user,username=username) 
@app.route("/accounts", methods=['GET', 'POST'])
def accounts():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, email FROM login_details")
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=['Username', 'Password', 'Email'])
    
    # Close the database connection
    conn.close()
    
    # Convert DataFrame columns into lists
    username_list = df['Username'].tolist()
    password_list = df['Password'].tolist()
    email_list = df['Email'].tolist() 
    return render_template("table.html", admin=admin, login_user=login_user, username=username, username_list=username_list, password_list=password_list, email_list=email_list)

if __name__ == '__main__':
    app.run(debug=True)
 
