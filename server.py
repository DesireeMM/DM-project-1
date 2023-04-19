"""Server for my app"""

from flask import (Flask, render_template, request, flash, session, redirect)
from model import connect_to_db, db
import crud

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def homepage():
    """View homepage"""

    return render_template('homepage.html')

@app.route("/login", methods=["POST"])
def user_login():
    """Handle user login"""

    user_email = request.form.get("email")
    user_password = request.form.get("password")

    current_user = crud.get_user_by_email(user_email)
    if current_user.password == user_password:
        session["user_id"] = current_user.user_id
        session["logged_in_email"] = current_user.email
        flash(f"Welcome, {current_user.fname}!")

    else:
        flash("Password incorrect. Please try again.")

    return redirect("/")

@app.route("/create-account", methods=["POST"])
def create_new_account():
    """Create a new user account"""
    user_email = request.form.get("email")
    user_password = request.form.get("password")
    user_fname = request.form.get("fname")
    user_lname = request.form.get("lname")
    user_phone = request.form.get("phone", None)

    if crud.get_user_by_email(user_email):
        flash("Email already taken. Please try again.")
        
    else:
        new_user = crud.create_user(user_fname, user_lname, user_email, user_password, user_phone)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully. Please log in.")

    return redirect("/")

@app.route("/events")
def view_events():
    """View a user's scheduled events"""

    logged_in_email = session.get("logged_in_email")
    current_user_id = session.get("user_id")
    current_user = crud.get_user_by_id(current_user_id)

    if logged_in_email is None:
        flash("You must log in to view events.")
        return redirect("/")
    else:
        all_events = crud.show_user_events(current_user_id)


    return render_template("all_events.html", all_events=all_events, current_user=current_user)

@app.route('/events/<event_id>')
def show_event(event_id):
    """Show details for a particular event"""

    event = crud.get_event_by_id(event_id)

    return render_template('event_details.html', event=event)

@app.route("/groups")
def view_groups():
    """View a user's groups"""

    logged_in_email = session.get("logged_in_email")
    current_user_id = session.get("user_id")
    current_user = crud.get_user_by_id(current_user_id)

    if logged_in_email is None:
        flash("You must log in to view your groups.")
        return redirect("/")
    else:
        all_groups = crud.show_user_groups(current_user_id)


    return render_template("all_groups.html", all_groups=all_groups, current_user=current_user)

@app.route('/groups/<group_id>')
def show_group(group_id):
    """Show details for a particular group"""

    group = crud.get_group_by_id(group_id)
    members = crud.show_group_members(group_id)

    return render_template('group_details.html', group=group, members=members)

@app.route("/availability")
def view_availability():
    """View Availability"""

    logged_in_email = session.get("logged_in_email")
    current_user_id = session.get("user_id")
    current_user = crud.get_user_by_id(current_user_id)
    availabilities = current_user.availabilities

    if logged_in_email is None:
        flash("You must log in to view availability.")
        return redirect("/")
    else:
        return render_template("availability.html", current_user=current_user, availabilities=availabilities)

@app.route("/add-availability", methods=["POST"])
def add_availability():
    """Add a new availability record"""

    current_user_id = session.get("user_id")
    current_user = crud.get_user_by_id(current_user_id)
    weekday = request.form.get("weekday")
    start = request.form.get("start-time")
    end = request.form.get("end-time")

    new_avail = crud.add_availability(current_user, weekday.title(), start, end)
    db.session.add(new_avail)
    db.session.commit()

    return redirect("/availability")



@app.route("/logout")
def user_logout():
    """Log current user out."""

    current_user = session.get("logged_in_email")
    current_user = crud.get_user_by_email(current_user)
    session.clear()
    flash(f"Logged out {current_user.fname}")

    return redirect("/")

if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)