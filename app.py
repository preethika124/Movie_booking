
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from datetime import datetime
import json

app = Flask(__name__)

# Secret key for session management
app.secret_key = "movie_booking_secret_key"

# Temporary in-memory storage
users = []
bookings = []

user_counter = 1
booking_counter = 1


# -------------------------------
# 1. Homepage
# -------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------
# 2. Signup
# -------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    global user_counter

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if user already exists
        existing_user = next(
            (u for u in users if u["email"] == email),
            None
        )

        if existing_user:
            flash("Email already registered!")
            return redirect(url_for("signup"))

        # Hash password
        hashed_password = generate_password_hash(password)

        user = {
            "id": user_counter,
            "name": name,
            "email": email,
            "password": hashed_password
        }

        users.append(user)
        user_counter += 1

        print("Current Users List:", json.dumps(users, indent=4))

        flash("Registration successful! Please login.")
        return redirect(url_for("login"))

    return render_template("signup.html")


# -------------------------------
# 3. Login
# -------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = next(
            (u for u in users if u["email"] == email),
            None
        )

        if user and check_password_hash(
            user["password"], password
        ):

            session["user"] = {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }

            print("Logged In User Session:", session["user"])

            flash("Login successful!")

            return redirect(url_for("home1"))

        flash("Invalid email or password!")
        return redirect(url_for("login"))

    return render_template("login.html")


# -------------------------------
# 4. Logout
# -------------------------------

@app.route("/logout")
def logout():

    session.pop("user", None)

    flash("Logged out successfully!")

    return redirect(url_for("index"))


# -------------------------------
# 5. Home after login
# -------------------------------

@app.route("/home1")
def home1():

    if "user" not in session:
        flash("Please login first!")
        return redirect(url_for("login"))

    return render_template(
        "home1.html",
        user=session["user"]
    )


# -------------------------------
# 6. About page
# -------------------------------

@app.route("/about")
def about():
    return render_template("about.html")


# -------------------------------
# 7. Contact page
# -------------------------------

@app.route("/contact_us")
def contact_us():
    return render_template("contact_us.html")


# -------------------------------
# 8. Booking page
# -------------------------------

@app.route("/b1")
def booking():

    if "user" not in session:
        flash("Please login to book tickets!")
        return redirect(url_for("login"))

    movie = request.args.get("movie")
    theater = request.args.get("theater")
    address = request.args.get("address")
    price = request.args.get("price")

    return render_template(
        "b1.html",
        movie=movie,
        theater=theater,
        address=address,
        price=price
    )


# -------------------------------
# 9. Submit ticket booking
# -------------------------------

@app.route("/tickets", methods=["POST"])
def tickets():

    global booking_counter

    if "user" not in session:
        flash("Please login first!")
        return redirect(url_for("login"))

    movie = request.form.get("movie")
    theater = request.form.get("theater")
    address = request.form.get("address")
    price = request.form.get("price")
    seats = request.form.getlist("seats")

    if not seats:
        flash("Please select at least one seat!")
        return redirect(request.referrer or url_for("home1"))

    # Calculate total price
    total_price = int(price) * len(seats)

    booking = {
        "booking_id": booking_counter,
        "user_id": session["user"]["id"],
        "movie": movie,
        "theater": theater,
        "address": address,
        "price": total_price,
        "seats": seats,
        "booking_time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    bookings.append(booking)
    booking_counter += 1

    print("Booking Added:", booking)

    print("All Bookings:", json.dumps(bookings, indent=4))

    return render_template(
        "tickets.html",
        booking=booking
    )


# -------------------------------
# 10. Run application
# -------------------------------

if __name__ == "__main__":
    app.run(debug=True)
