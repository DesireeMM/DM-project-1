"""Server for my app"""

import smtplib
import os
from datetime import datetime
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
    if current_user and current_user.password == user_password:
        session["user_id"] = current_user.user_id
        session["logged_in_email"] = current_user.email
        session["notifications"]=current_user.notifications
        print(current_user.notifications)
        print(session["notifications"])
        notifications_count = len(current_user.notifications)
        session["notifications_count"] = notifications_count
        flash(f"Welcome, {current_user.fname}!")
        return redirect("/dashboard")

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

@app.route("/dashboard")
def view_dashboard():
    """View User Dashboard"""
    current_user_id = session.get("user_id")
    current_user = crud.get_user_by_id(current_user_id)

    unread_notifications = []

    for notification in current_user.notifications:
        if notification.read_status is False:
            unread_notifications.append(notification.message)
            notification.read_status = True
#update notification count in the session
            db.session.commit()
        elif notification.read_status is True:
            if notification.message in unread_notifications:
                unread_notifications.remove(notification.message)

    
    return render_template("dashboard.html",
                           current_user=current_user,
                           unread_notifications=unread_notifications)

@app.route("/events")
def view_events():
    """View a user's scheduled events"""

    logged_in_email = session.get("logged_in_email")
    current_user_id = session.get("user_id")
    current_user = crud.get_user_by_id(current_user_id)
    current_datetime = datetime.now()

    if logged_in_email is None:
        flash("You must log in to view events.")
        return redirect("/")
    else:
        all_events = crud.show_user_events(current_user_id)


    return render_template("all_events.html",
                           all_events=all_events,
                           current_user=current_user,
                           current_datetime=current_datetime)

@app.route('/events/<event_id>')
def show_event(event_id):
    """Show details for a particular event"""

    event = crud.get_event_by_id(event_id)
    group = crud.get_group_by_id(event.group_id)
    group_name = group.name
    event_host = crud.get_user_by_id(event.created_by)

    return render_template("event_details.html",
                           event=event,
                           group_name=group_name,
                           event_host=event_host)

@app.route('/create-event')
def create_event():
    """Show form for creating a new event"""
    current_user_id = session.get("user_id")
    poss_groups = crud.show_user_groups(current_user_id)

    return render_template("create_event.html",
                           current_user_id=current_user_id,
                           poss_groups=poss_groups)

@app.route('/add-event', methods=["POST"])
def add_event():
    """Add event to database"""
    current_user_id = session.get("user_id")
    group_id = request.form.get("group")
    name = request.form.get("name")
    desc = request.form.get("description")

    new_event = crud.create_event(created_by=current_user_id,
                                  group_id=group_id,
                                  name=name,
                                  description=desc)
    db.session.add(new_event)
    db.session.commit()

    event_id = new_event.event_id

    group_members = crud.show_group_members(group_id)
    for member in group_members:
        crud.add_event(member.email, event_id)

    return redirect(f"/events/{event_id}")

@app.route("/events-personal")
def view_personal_calendar():
    """Display a user's personal event calendar"""
    
    return render_template("calendar.html")

@app.route("/update-event/<event_id>")
def update_event(event_id):
    """Display form to update a particular event."""
    target_event = crud.get_event_by_id(event_id)
    group_id = target_event.group_id
    availabilities = crud.create_availability_ref(group_id)
    best_day = crud.get_best_weekday(availabilities)
    attendees, start_time, end_time = crud.get_time_range_loop(availabilities, best_day)
    best_start_time, best_end_time = crud.get_best_range(availabilities, best_day, start_time, end_time)

    return render_template("update_event.html",
                           event=target_event,
                           availabilities=availabilities,
                           best_day=best_day,
                           attendees=attendees,
                           start_time=best_start_time,
                           end_time=best_end_time)

@app.route("/event-updated", methods=["POST"])
def show_updated_event():
    """Show event details after updating"""
    target_event_id = request.form.get("event_id")
    target_event = crud.get_event_by_id(target_event_id)
    name = request.form.get("new-name")
    desc = request.form.get("new-desc")
    activity = request.form.get("activity")
    date = request.form.get("date")
    time = request.form.get("time")
    event_datetime = date + " " + time

    if not name:
        name = target_event.name
    if not desc:
        desc = target_event.description
    if not activity:
        activity = target_event.activity
    if not date or not time:
        event_datetime = target_event.datetime
        

    crud.update_event(target_event_id,
                      name=name,
                      datetime=event_datetime,
                      activity=activity,
                      description=desc)
    
    notification_message = f"{target_event.name} on {target_event.datetime} has been updated."
    
    for user in target_event.users:
        new_notification = crud.add_notification(event_id=target_event_id,
                                                 user_id=user.user_id,
                                                 message=notification_message,
                                                 read_status=False)
        db.session.add(new_notification)
        db.session.commit()

    return redirect(f"/events/{target_event_id}")

# @app.route("/send-event-update")
# def send_event_update():
#     """Display form to send out a notification"""
#     current_user_id = session.get("user_id")
#     poss_events = crud.show_hosted_events(current_user_id)


#     return render_template("send_update.html",
#                            poss_events=poss_events)

# @app.route("/send-update", methods=["POST"])
# def send_update_email():
#     """Handle sending an update email"""

#     event_id = request.form.get("event")
    
#     current_event = crud.get_event_by_id(event_id)

#     recipients = []
#     for user in current_event.users:
#         recipients.append(user.email)

#     sender_email = "whentochill@yahoo.com"
#     my_password = os.environ['GMAIL_PASSWORD']
#     message = "Trying this"

#     with smtplib.SMTP("smtp.mail.yahoo.com", 465) as connection:
#         context = smtplib.ssl.create_default_context()
#         connection.starttls(context=context)
#         connection.login(sender_email, my_password)
#         connection.sendmail(sender_email, sender_email, message)
#         connection.quit()


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


    return render_template("all_groups.html",
                           all_groups=all_groups,
                           current_user=current_user)

@app.route("/groups/<group_id>")
def show_group(group_id):
    """Show details for a particular group"""

    group = crud.get_group_by_id(group_id)
    members = crud.show_group_members(group_id)
    group_creator = crud.get_user_by_id(group.created_by)

    return render_template('group_details.html',
                           group=group,
                           members=members,
                           group_creator=group_creator)

@app.route("/groups/<group_id>/availability")
def show_group_availability(group_id):
    """Show availability details for a particular group"""

    group = crud.get_group_by_id(group_id)
    creator = crud.get_user_by_id(group.created_by)
    members = crud.show_group_members(group_id)
#sort the availabilities before displaying them here
    return render_template('group_avail_details.html',
                           group=group,
                           creator=creator,
                           members=members)

@app.route("/create-group")
def create_group():
    """Show form for creating a new group"""
    current_user_id = session.get("user_id")

    return render_template("create_group.html",
                           current_user_id=current_user_id)

@app.route("/add-group", methods=["POST"])
def add_group():
    """Add group to database"""
    current_user_id = session.get("user_id")
    current_email = session.get("logged_in_email")
    group_name = request.json.get("group_name")
    group_members = request.json.get("group_members")

    new_group = crud.create_group(created_by=current_user_id,
                                  name=group_name)
    
    db.session.add(new_group)
    db.session.commit()
    
    group_id = new_group.group_id
    crud.add_user(current_email, group_id)

    for email in group_members:
        member = crud.get_user_by_email(email)
        if not member:
            flash(f"{email} could not be added.")
        else:
            crud.add_user(email, group_id)
            flash(f"{email} was added to {new_group.name}")
    return {
        "success": True,
        "status": "Successfully formed group!",
        "redirect": f"/groups/{group_id}"
    }

@app.route("/new-group-member", methods=["POST"])
def add_member():
    """Handle adding a new member to a group."""

    group_id = request.form.get("group_id")
    user_email = request.form.get("user_email")
    new_member = crud.get_user_by_email(user_email)
    all_users = crud.get_users()
    group_members = crud.show_group_members(group_id)

    if new_member in group_members:
        flash("Member already in group.")
    elif new_member in all_users:
        crud.add_user(user_email, group_id)
        flash("New member added successfully.")
    else:
        flash("User not found. Please make sure to enter a valid email address.")

    return redirect(f"/groups/{group_id}")

@app.route("/availability")
def view_availability():
    """View Availability"""

    logged_in_email = session.get("logged_in_email")
    current_user_id = session.get("user_id")
    current_user = crud.get_user_by_id(current_user_id)
    availabilities = current_user.availabilities
#sort availabilities using lambda function here
#use a dictionary to match weekdays to numbers
    if logged_in_email is None:
        flash("You must log in to view availability.")
        return redirect("/")
    else:
        return render_template("availability.html",
                               current_user=current_user,
                               availabilities=availabilities)

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

@app.route("/update-availability", methods=["POST"])
def update_availability():
    """Update a user's availability"""

    avail_id = request.json["avail_id"]
    new_start = request.json["new_start"]
    new_end = request.json["new_end"]

    crud.update_availability(avail_id, new_start, new_end)

    return {
        "success": True,
        "status": "You have updated your availability."
    }

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
