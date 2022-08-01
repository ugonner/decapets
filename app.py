from ast import Return
from collections import UserString
from datetime import datetime
from email import message
# import mathfla
# from nis import cat
import os
from random import random
import re
from time import strftime
from turtle import update
from warnings import catch_warnings
from xml.etree.ElementTree import C14NWriterTarget
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import  check_password_hash, generate_password_hash
from helpers import apology, login_required, usd
#from werkzeug import secure_filename
import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
#db = sqlite3.connect('decapets.db', check_same_thread=False)
db = SQL("sqlite:///decapets.db")

#template globals
categories = db.execute("SELECT * FROM category")
subcategories = db.execute("SELECT * FROM subcategory")

app.jinja_env.globals["categories"] = categories
app.jinja_env.globals["subcategories"] = subcategories

# Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/about_us")
def aboutus ():
    return render_template("aboutus.html")
    

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # Ensure username was submitted
        if not request.form.get("user_name"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)


        # Query database for username
        rows = db.execute("SELECT * FROM user WHERE user_name = ? or email = ?", request.form.get("user_name"),request.form.get("user_name"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")+"bona") :
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_data"] = rows[0]

        #check if user is admin
        is_admin = db.execute("SELECT user_id FROM admin WHERE user_id = ?", session["user_id"])
        if is_admin:
            session["is_admin"] = True

        # Redirect user to home page
        # return redirect("/")
        return redirect ("/user?a=get_user")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == 'GET':
        return render_template('register.html')


    if request.method == "POST":
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        email = request.form.get('email')
        role = request.form.get('role')
        
        #validating inputs name password and email
        if not user_name:
            return apology("Enter a username")

        elif not password or not password == confirmation:
            return apology("Enter a password or passwords did not match")

        else:
            #check if email exists already
            email_in_db = db.execute("SELECT count(*) AS count FROM user WHERE email = ?", email)
            if email_in_db[0]["count"] > 0:
                flash("Email already exist")
                return redirect("/register")

            password = password + 'bona'
            password = generate_password_hash(password, 'pbkdf2:sha256', 4)

            #insert user details into database
            user_id = db.execute("INSERT INTO user (email, password, user_name, role) VALUES (?,?,?,?)", email, password, user_name, role)
            if user_id > 0:
                
                return redirect('/user?a=get_user&id='+ str(user_id))
                

    flash("Enter a username")
    return redirect ("/register")



# ADMIN
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():


    message = ""
    if request.method == "GET":
        action = request.args.get("a")
        if action == "make_admin":
            user_id = request.args.get("user_id")
            try:

                insert = db.execute("INSERT INTO admin (user_id) VALUES (?)", user_id)
                if insert > 0:
                    message = "Admin successfully created"
                else:
                    message = "unable to make admin"
            except:
                message = "User is already an admin"
                return apology(message)


    if request.method == "POST":
        action = request.form.get("a")
        if action == "update_booking_status":
            s = request.form.get("booking_status")
            sr = request.form.get("booking_status_report")
            id = request.form.get("id")
            
            if s is None or sr is None or id is None:
                message = "Supply all requied paramenters"
            
            updated = db.execute("UPDATE booking SET booking_status = ?, booking_status_report = ? WHERE id=?", s, sr, id)
            message = "Status Updated Successfully"
            #EMAIL USER (CLIENT)
        
       
        # for updating pet_report
        if action == "update_pet_report_status":
            ps = request.form.get("pet_status")
            psc = request.form.get("pet_status_comment")
            id = request.form.get("id")
            
            if ps is None or psc is None or id is None:
                message = "please supply all needed paramenters"
            
            updated = db.execute("UPDATE pet_report SET pet_status = ?, pet_status_comment = ? WHERE id=?", ps, psc, id)
            message = "Status Updated Successfully"
            #EMAIL USER (CLIENT)
            
    
    pets = db.execute("SELECT pet.*, category.name as category_name, subcategory.name as subcategory_name, shelter_home_name FROM pet JOIN category ON pet.category_id = category.id JOIN subcategory ON category.id = subcategory.category_id JOIN shelter_home ON pet.shelter_home_id = shelter_home.id ORDER BY pet.id DESC")
    bookings = db.execute("SELECT booking.*, user.user_name, user.id as user_id FROM booking JOIN user ON booking.user_id = user.id ORDER BY booking.id DESC")
    pet_reports = db.execute("SELECT pet_report.*, category.name as category_name, subcategory.name as subcategory_name, user_name FROM pet_report JOIN user ON pet_report.user_id = user.id JOIN category ON pet_report.category_id = category.id JOIN subcategory ON category.id = subcategory.category_id ORDER BY pet_report.id DESC")
    shelter_homes = db.execute("SELECT * FROM shelter_home ORDER BY id DESC")
    
    return render_template("admin/index.html", bookings = bookings, pets=pets, pet_reports=pet_reports, shelter_homes= shelter_homes, message=message)



#routes for handling actions on pETS: 
@app.route("/pets", methods=["GET", "POST"])
def pets():
    if request.method == "GET":
        action = request.args.get("a")
        if action == "add_pet":
            shelter_homes = db.execute("SELECT id, shelter_home_name FROM shelter_home")
            return render_template("admin/add_pet_form.html", shelter_homes = shelter_homes)

        
        if action == 'get_pets':
            pty = request.args.get("pty")
            val = request.args.get("val")

            if pty is not None:

                query = "SELECT pet.*, category.name AS category_name, subcategory.name AS subcategory_name, shelter_home_name FROM pet JOIN category ON pet.category_id = category.id JOIN subcategory ON subcategory.id = pet.subcategory_id JOIN shelter_home ON shelter_home.id = pet.shelter_home_id WHERE pet."+ pty + " = "+ val
            
                pets = db.execute(query)
                pets = db.execute("SELECT pet.*, category.name AS category_name, subcategory.name AS subcategory_name, shelter_home_name FROM pet JOIN category ON pet.category_id = category.id JOIN subcategory ON subcategory.id = pet.subcategory_id JOIN shelter_home ON shelter_home.id = pet.shelter_home_id WHERE pet.category_id = ?", val)
                
            else:
                pets = db.execute("SELECT pet.*, category.name AS category_name, subcategory.name AS subcategory_name, shelter_home_name FROM pet JOIN category ON pet.category_id = category.id JOIN subcategory ON subcategory.id = pet.subcategory_id JOIN shelter_home ON shelter_home.id = pet.shelter_home_id ORDER BY pet.id DESC")
                
            message = "No pets in this category yet"
            if pets:
                message = "Your Pets Are Here"
            return render_template("pets.html",pets=pets, message = message)
    
        #search block
        if action == "search":
            val = request.args.get("val")
            pets = db.execute("SELECT pet.*, category.name AS category_name, subcategory.name AS subcategory_name, shelter_home_name FROM pet JOIN category ON pet.category_id = category.id JOIN subcategory ON subcategory.id = pet.subcategory_id JOIN shelter_home ON shelter_home.id = pet.shelter_home_id WHERE pet.pet_name LIKE ? OR  pet.pet_description LIKE ? OR  category.name LIKE ? OR  subcategory.name LIKE ? OR  shelter_home_name LIKE ?", val, val, val, val, val)
            message = "Your Pets Are Here"
            return render_template("pets.html",pets=pets, message = message)
        
        #view a particular pet
        if action == "get_pet":
            id = request.args.get("id")
            pets = db.execute("SELECT pet.*, category.name AS category_name, subcategory.name AS subcategory_name, shelter_home_name FROM pet JOIN category ON pet.category_id = category.id JOIN subcategory ON subcategory.id = pet.subcategory_id JOIN shelter_home ON shelter_home.id = pet.shelter_home_id WHERE pet.id = ?", id)
            message = "Your Pet Is Here"
            return render_template("pet.html",pet=pets[0], message = message)
        
    if request.method == "POST":
        name = request.form.get("pet_name")
        price = request.form.get("price")
        description = request.form.get("description")
        category_id = request.form.get("category_id")
        subcategory_id = request.form.get("subcategory_id")
        user_id = session["user_id"]
        shelter_home_id = request.form.get("shelter_home_id")
        age = request.form.get("age")
        status = "Available"

        upload_date = datetime.datetime.now()
        upload_date = upload_date.strftime("%Y-%m-%d %H:%M")
        time_str = datetime.datetime.now()
        time_str = time_str.strftime("%Y%m%d%H%M")

        pet_image = request.files["pet_image_url"]
        pet_image_url =  "static/images/pets/"+time_str + pet_image.filename
        pet_image.save(pet_image_url)

        inserted = db.execute("INSERT INTO pet (pet_name, pet_description, category_id, subcategory_id, user_id, shelter_home_id, pet_status, pet_image_url, upload_date, age, price) VALUES(?,?,?,?,?,?,?,?,?,?,?)", name, description, category_id, subcategory_id, user_id, shelter_home_id, status, pet_image_url, upload_date, age, price)
        if inserted > 0:
            return render_template("admin/add_pet_form.html", message = "You have successfully uploaded a pet")

    



#ROUTES FOR PET REPORTS
@app.route("/pet_reports", methods=["GET", "POST"])
@login_required
def pet_reports():
    """Sell shares of stock"""
    if request.method == "GET":
        action = request.args.get("a")
        if action == "add_pet_report":
            shelter_homes = db.execute("SELECT id, shelter_home_name FROM shelter_home")
            return render_template("admin/add_pet_report_form.html", shelter_homes = shelter_homes)

        if action == "get_pet_reports":
            pty = request.args.get("pty")
            val = request.args.get("val")

            if pty:
                pets = db.execute("SELECT pet_report.*, category.name as category_name, subcategory.name as subcategory_name, user_name FROM pet_report JOIN user ON pet_report.user_id = user.id JOIN category ON pet_report.category_id = category.id JOIN subcategory ON category.id = subcategory.category_id WHERE pet_report."+pty+"="+val+" ORDER BY pet_report.id DESC")
                return render_template("pets.html", pets=pets)
            return apology("No reports yet ")

    if request.method == "POST":
        name = request.form.get("pet_name")
        description = request.form.get("description")
        category_id = request.form.get("category_id")
        subcategory_id = request.form.get("subcategory_id")
        user_id = session["user_id"]
        shelter_home_id = request.form.get("shelter_home_id")
        age = request.form.get("age")
        status = request.form.get("pet_status")
        address = request.form.get("address")
        
        upload_date = datetime.datetime.now()
        upload_date = upload_date.strftime("%Y-%m-%d %H:%M")
        time_str = datetime.datetime.now()
        time_str = time_str.strftime("%Y%m%d%H%M")

        pet_image = request.files["pet_image_url"]
        pet_image_url =  "static/images/pet_reports/"+time_str + pet_image.filename
        pet_image.save(pet_image_url)

        inserted = db.execute("INSERT INTO pet_report (pet_name, description, category_id, subcategory_id, user_id, shelter_home_id, pet_status, pet_image_url, upload_date, age, address) VALUES(?,?,?,?,?,?,?,?,?,?,?)", name, description, category_id, subcategory_id, user_id, shelter_home_id, status, pet_image_url, upload_date, age, address)
        if inserted > 0:
            return redirect("/")


                

    return apology("TODO")


#route for populating pet categories
@app.route("/pet_categories", methods=["GET", "POST"])
@login_required
def pet_categories():

    if request.method == "GET":
        return render_template("admin/pet_categories.html")

    if request.method == "POST":
        cn = request.form.get("name")
        c_i = request.form.get("category_id")
        
        if c_i  and int(c_i) > 0:
            inserted = db.execute("INSERT INTO subcategory (name, category_id) VALUES (?, ?)", cn, c_i)
            if inserted > 0:
                message = "Subcategory successfully created"
        else:
            inserted = db.execute("INSERT INTO category (name) VALUES (?)", cn)
            if inserted:
                message = "Main Category successfully created"
            
        return render_template("admin/pet_categories.html", message=message)
                


#ROUTES FOR SHELTER HOMES
@app.route("/shelter_homes", methods=["GET", "POST"])
@login_required
def shelter_home():
    if request.method == "GET":
        action = request.args.get("a")
        if action == "add_shelter_home":
            return render_template("admin/add_shelter_home_form.html")

        if action == "get_shelter_homes":
            return render_template("shelter_homes.html")

    if request.method == "POST":
        sn = request.form.get("shelter_home_name")
        saddress = request.form.get("address")
        se = request.form.get("email")
        sd = request.form.get("description")

        srd = datetime.datetime.now()
        srd = srd.strftime("%Y %m %d %H:%M:%S")

        if sn is None or saddress is None or se is None:
            return render_template("admin/add_shelter_home_form.html", message="all fields are required")

        else:
            try:

                inserted = db.execute("INSERT INTO shelter_home (shelter_home_name, email, address, description, registration_date) VALUES (?,?,?,?,?)", sn, se, saddress, sd, srd)
                if inserted > 0:
                    message = "Home created"
                else:
                    message = "Failed"
            except:
                message = "Already Registered Email Accound"

            return render_template("admin/add_shelter_home_form.html", message=message)
        
                
    return apology("Error")
    


#routes for bookings, add to cart; check out; and payment
@app.route("/bookings", methods=["GET", "POST"])
@login_required
def bookings():
    if request.method == "GET":
        action = request.args.get("a")
        if action == "add_booking":
            return render_template("admin/booking_form.html")
        
        if action == "add_to_cart":
            
            #create session for cart if not exist
            pet_id = request.args.get("id")
            pet_price = request.args.get("price")
            #check if cart already exists in session dictionary
            #if not; initialixe session['cart'] and add the pet id to it
            if not "cart" in session.keys():
                session["cart"] = {
                    "pet_ids": [],
                    "total_cost": 0
                }
                session["cart"]["pet_ids"].append(pet_id)
                session["cart"]["total_cost"] = pet_price
            #if cart already exist; check if pet is NOT already in cart and ADD it     
            elif 'pet_ids' in session["cart"].keys() and (not pet_id in session["cart"]["pet_ids"]):
                session["cart"]["pet_ids"].append(pet_id)
                session["cart"]["total_cost"] += pet_price

            else:
                flash("Already In cart", "Failure")
                return redirect("/pets?a=get_pets")

            #get all cart pets' details 
            pet_id_array = session["cart"]["pet_ids"]

            pets = db.execute("SELECT pet.*, category.name AS category_name, subcategory.name AS subcategory_name, shelter_home_name FROM pet JOIN category ON pet.category_id = category.id JOIN subcategory ON pet.subcategory_id = subcategory.id JOIN shelter_home ON pet.shelter_home_id = shelter_home.id WHERE pet.id IN (?)", pet_id_array)
            return render_template("add_booking_form.html", pets=pets)


        if action == "clear_booking":
            del session["cart"]
            flash("Cart cleared")
            return redirect("/")

        if action == "pay":
            id = request.args.get("id")
            update_booking_status = db.execute("UPDATE booking SET payment_status = 'Paid' WHERE id = ? AND user_id = ?", id, session["user_id"])
            cart_id = db.execute("SELECT cart_id FROM booking WHERE id = ?", id)
            if cart_id:
                update_pet_status = db.execute("UPDATE pet SET pet_status = 'Sold' WHERE pet.id IN (SELECT pet_id FROM cart_pet WHERE cart_id = ?)", cart_id[0]["cart_id"])
            flash("Payment Successful, Your pet will be shipped")
            return redirect("/user?a=get_user")

        if action == "get_cart":
            cart_id = request.args.get("cart_id")
            pets = db.execute("SELECT pet.*, category.name AS category_name, subcategory.name as subcategory_name, shelter_home_name FROM cart JOIN cart_pet ON cart.id = cart_pet.cart_id JOIN pet ON cart_pet.pet_id = pet.id JOIN category ON category.id = pet.category_id JOIN subcategory ON pet.subcategory_id = subcategory.id JOIN shelter_home ON pet.shelter_home_id = shelter_home.id WHERE cart_pet.cart_id = ?", cart_id)
            return render_template("add_booking_form.html", pets=pets)
                
        if action == "get_bookings":
            pty = request.args.get("pty")
            val = request.args.get("val")
            bookings = db.execute("SELECT booking.*, user.user_name, user.id as user_id FROM booking JOIN user ON booking.user_id = user.id WHERE booking."+pty+"='"+val+"' ORDER BY booking.id DESC")
    

            return render_template("admin/bookings.html", bookings=bookings)

    if request.method == "POST":
        action = request.form.get("a")
        if action == "add_booking":
            ba = request.form.get("booking_address")

            bsd = datetime.datetime.now()
            bsd = bsd.strftime("%Y-%m-%d %H:%M:%S")
            bs = "Under Verification"
            bsr = "Your request is being reviewed"
            ps = "UnPaid"

            ui = session["user_id"]
            c = session["cart"]
            cp = session["cart"]["pet_ids"]

            #Add item to cart table 1
            cart_id = db.execute("INSERT INTO cart (user_id, total_cost, cart_date) VALUES (?,?,?)", ui, c["total_cost"], bsd)
            
            for p in cp:
                insert = db.execute("INSERT INTO cart_pet (cart_id, pet_id, pet_quantity) VALUES (?,?,?)", cart_id, p, 1)
                update_pet_availability = db.execute("UPDATE pet SET pet_status = 'Booked' WHERE id = ?", p)
            book = db.execute("INSERT INTO booking (cart_id, user_id, booking_status, booking_status_report, total_cost, booking_address, booking_status_date, payment_status) VALUES (?,?,?,?,?,?,?,?)", cart_id, ui, bs, bsr, c["total_cost"], ba, bsd, ps)
            if book:
                del session["cart"]
                flash("Pet Booked successfully", "success")

            return redirect("/user?a=get_user")
    return apology("No jokes")



#ROUTE FOR USER
@app.route("/user", methods=["GET", "POST"])
@login_required
def user():
    if request.method == "GET":
        action = request.args.get("a")
        if action == "get_user":
            user_id = request.args.get("id")
            if not user_id:
                user_id = session["user_id"]

            bookings = db.execute("SELECT booking.* FROM booking JOIN user ON user.id = booking.user_id WHERE user_id = ? ORDER BY booking.id DESC ", user_id)
            pet_reports = db.execute("SELECT pet_report.* FROM pet_report JOIN user ON user.id = pet_report.user_id WHERE user_id = ? ORDER BY pet_report.id DESC", user_id)
            user = db.execute("SELECT * FROM user WHERE id = ?", user_id)
            return render_template("user_profile.html", pet_reports=pet_reports, bookings=bookings, user=user)
        
            
        if action == "get_users":
            users = db.execute("SELECT * FROM user ORDER BY id DESC")
            if users:
                message = "users got"
            else:
                message = "No users got "
            return render_template("admin/users.html", users=users, message=message)
        
        if action == "update_user":
            user_id = request.args.get("user_id")
            role = request.args.get("role")

            user = db.execute("UPDATE user SET role = ? WHERE id = ?", role, user_id)
            if user:
                message = "user"
            else:
                message = "No users got "
            flash(message)
            return redirect("/user?a=get_user&id="+user_id)