"""Server for my app"""

import os
from datetime import datetime
import json
import requests
from flask import (Flask, render_template, request, flash, session, redirect, jsonify)
from model import connect_to_db, db
import crud
import cloudinary.uploader
from passlib.hash import argon2

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

API_KEY = os.environ["GMAPS_API_KEY"]
CLOUDINARY_KEY = os.environ["CLOUDINARY_KEY"]
CLOUDINARY_SECRET = os.environ["CLOUDINARY_SECRET"]
CLOUD_NAME = "dkraqtb6p"

weekday_dict = {"Sunday": 0,
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6}

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

    if not current_user:
        flash("Account does not exist. Please try again or Create New Account")
        return redirect("/")

    elif current_user and argon2.verify(user_password, current_user.password):
        session["user_id"] = current_user.user_id
        session["logged_in_email"] = current_user.email
        return redirect("/dashboard")

    else:
        flash("Password incorrect. Please try again.")
        return redirect("/")

@app.route("/new-account")
def new_account_form():
    """Display form for creating a new user account."""

    return render_template("create_account.html")

@app.route("/create-account", methods=["POST"])
def create_new_account():
    """Create a new user account"""
    user_email = request.form.get("email")
    user_password = request.form.get("password")
    user_pw_confirm = request.form.get("password-confirm")
    user_fname = request.form.get("fname")
    user_lname = request.form.get("lname")
    user_phone = request.form.get("phone", None)

    if crud.get_user_by_email(user_email):
        flash("Email already taken. Please try again.")
    elif user_password != user_pw_confirm:
        flash("Passwords don't match. Please try again.")
    else:
        hashed_pw = crud.hash_password(user_password)
        new_user = crud.create_user(user_fname, user_lname, user_email, hashed_pw, user_phone)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully. Please log in.")

    return redirect("/")

@app.route("/dashboard")
def view_dashboard():
    """View User Dashboard"""
    logged_in_email = session.get("logged_in_email")
    if logged_in_email is None:
        flash("You must log in to view your dashboard.")
        return redirect("/")
    current_user_id = session.get("user_id")
    current_user = crud.get_user_by_id(current_user_id)
    availabilities = current_user.availabilities
    current_datetime = datetime.now()

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
                           unread_notifications=reversed(unread_notifications),
                           availabilities=availabilities,
                           current_datetime=current_datetime)

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

    notifications = current_user.notifications

    return render_template("all_events.html",
                           all_events=all_events,
                           current_user=current_user,
                           current_datetime=current_datetime,
                           notifications=notifications)

@app.route('/events/<event_id>')
def show_event(event_id):
    """Show details for a particular event"""

    event = crud.get_event_by_id(event_id)
    group = crud.get_group_by_id(event.group_id)
    group_name = group.name
    event_host = crud.get_user_by_id(event.created_by)
    current_user = crud.get_user_by_id(session["user_id"])

    return render_template("event_details.html",
                        event=event,
                        group_name=group_name,
                        event_host=event_host,
                        current_user=current_user,)


@app.route('/delete-event', methods=["POST"])
def delete_event():
    """Delete a particular event"""

    event_id = request.json.get("event_id")
    target_event = crud.get_event_by_id(event_id)
    crud.delete_event(event_id)

    for member in target_event.users:
        notification = crud.add_notification(member.user_id,
                                             message=f"{target_event.name} has been deleted.",
                                             read_status=False)
        db.session.add(notification)
        db.session.commit()
    
    notifications = crud.get_event_notifications(event_id)
    for notification in notifications:
        db.session.delete(notification)
        db.session.commit()

    return jsonify({
        "status": f"You have deleted {target_event.name}.",
        "redirect": '/events'
    })

@app.route("/leave-event", methods=["POST"])
def leave_event():
    """Remove a user from a particular event"""

    user_id = session["user_id"]
    event_id = request.json.get("event_id")
    target_event = crud.get_event_by_id(event_id)
    event_host_id = target_event.created_by
    target_user = crud.get_user_by_id(user_id)

    crud.update_user_events(user_id, event_id)

    notification = crud.add_notification(user_id=event_host_id,
                          event_id=event_id,
                          message = f"{target_user.fname} cannot attend {target_event.name}.",
                          read_status = False)
    db.session.add(notification)
    db.session.commit()


    return ({
        "status": f"You will not be attending {target_event.name}.",
        "redirect": "/events"
    })

@app.route('/create-event')
def create_event():
    """Show form for creating a new event"""

    current_user_id = session.get("user_id")
    
    if not current_user_id:
        flash("You must be logged in to create events.")
        return redirect("/")
    
    poss_groups = crud.show_user_groups(current_user_id)

    return render_template("create_event.html",
                           current_user_id=current_user_id,
                           poss_groups=poss_groups)

# @app.route('/api/group-members', methods=["POST"])
# def display_group_members():
#     """Display group member checklist on create event form"""
    
#     group_id = request.json.get("group_id")

#     group_members = crud.show_group_members(group_id)

#     members = []
#     for member in group_members:
#         members.append({
#             "id": member.user_id,
#             "name": member.fname,
#             })

#     return jsonify(members)

@app.route('/add-event', methods=["POST"])
def add_event():
    """Add event to database"""
    current_user_id = session.get("user_id")
    group_id = request.form.get("group")
    name = request.form.get("name")
    desc = request.form.get("description")
    activity = request.form.get("activity")
    event_date = request.form.get("date")
    event_time = request.form.get("time")
    event_datetime = event_date + " " + event_time

    if not event_date or not event_time:
        event_datetime = None

    new_event = crud.create_event(created_by=current_user_id,
                                  group_id=group_id,
                                  name=name,
                                  description=desc,
                                  activity=activity,
                                  datetime=event_datetime)
    db.session.add(new_event)
    db.session.commit()

    event_id = new_event.event_id

    notification_message = f"You have been invited to {new_event.name}."

    group_members = crud.show_group_members(group_id)
    for member in group_members:
        crud.add_event(member.email, event_id)
        if member.user_id != current_user_id:
            new_notification = crud.add_notification(event_id=event_id,
                                                    user_id=member.user_id,
                                                    message=notification_message,
                                                    read_status=False)
            db.session.add(new_notification)
            db.session.commit()
        else:
            flash("You have successfully created a new event!")

    return redirect(f"/events/{event_id}")

@app.route("/api/events")
def grab_personal_events():
    """Store a user's event information in JSON"""

    current_user = crud.get_user_by_id(session["user_id"])
    personal_events = current_user.events

    events = []
    for event in personal_events:
        if event.datetime:
            event_datetime = event.datetime
            event_iso_datetime = event_datetime.isoformat()

            events.append({
                "id": event.event_id,
                "start": event_iso_datetime,
                "title": event.name,
                "url": f"/events/{event.event_id}",
                "display": "auto"
            })

    return jsonify(events)

@app.route("/events-personal")
def view_personal_calendar():
    """Display a user's personal event calendar"""
    
    current_user_id = session.get("user_id")
    
    if not current_user_id:
        flash("You must be logged in to view your calendar.")
        return redirect("/")
    
    return render_template("calendar.html")

@app.route("/update-event/<event_id>")
def update_event(event_id):
    """Display form to update a particular event."""
    target_event = crud.get_event_by_id(event_id)
    group_id = target_event.group_id
    availabilities = crud.create_availability_ref(group_id)
    best_day = crud.get_best_weekday(availabilities)
    attendees, start_time, end_time = crud.get_time_range_loop(availabilities, best_day)
    best_start_time, best_end_time = crud.get_best_range(availabilities,
                                                         best_day,
                                                         start_time,
                                                         end_time)
    start_formatted = best_start_time.strftime("%-I:%M %p")
    end_formatted= best_end_time.strftime("%-I:%M %p")

    return render_template("update_event.html",
                           event=target_event,
                           availabilities=availabilities,
                           best_day=best_day,
                           attendees=attendees,
                           start_time=start_formatted,
                           end_time=end_formatted,
                           group_id=group_id)

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

    date_str = target_event.datetime.strftime("%m/%d/%Y")
    time_str = target_event.datetime.strftime("at %-I:%M %p")

    notification_message = f"{target_event.name} ({date_str} {time_str}) has been updated."

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
        group_photos = []
        for group in all_groups:
            if group.group_img:
                group_photos.append(group)


    return render_template("all_groups.html",
                           all_groups=all_groups,
                           current_user=current_user,
                           group_photos=group_photos)

@app.route("/groups/<group_id>")
def show_group(group_id):
    """Show details for a particular group"""

    group = crud.get_group_by_id(group_id)
    members = crud.show_group_members(group_id)
    group_creator = crud.get_user_by_id(group.created_by)
    current_user = crud.get_user_by_id(session["user_id"])

    return render_template('group_details.html',
                           group=group,
                           members=members,
                           group_creator=group_creator,
                           current_user=current_user)

@app.route("/delete-group", methods=["POST"])
def delete_group():
    """Delete an entire group from the database"""

    group_id = request.json.get("group_id")
    target_group = crud.get_group_by_id(group_id)
    members = target_group.users

    for member in members:
        notification = crud.add_notification(member.user_id,
                                             message=f"{target_group.name} has been deleted.",
                                             read_status=False)
        db.session.add(notification)
        db.session.commit()

    notifications = crud.get_group_notifications(group_id)
    for notification in notifications:
        db.session.delete(notification)
        db.session.commit()

    crud.delete_group(group_id)


    return jsonify({
        "status": f"You have deleted {target_group.name}.",
        "redirect": "/groups"
    })

@app.route("/leave-group", methods=["POST"])
def leave_group():
    """Remove a user from a particular group"""

    user_id = session["user_id"]
    group_id = request.json.get("group_id")
    target_group = crud.get_group_by_id(group_id)

    crud.update_user_groups(user_id, group_id)

    return ({
        "status": f"You have left {target_group.name}.",
        "redirect": "/groups"
    })

@app.route("/groups/<group_id>/availability")
def show_group_availability(group_id):
    """Show availability details for a particular group"""

    group = crud.get_group_by_id(group_id)
    session["current_group_id"] = group_id
    creator = crud.get_user_by_id(group.created_by)
    members = crud.show_group_members(group_id)

    return render_template('group_avail_details.html',
                           group=group,
                           creator=creator,
                           members=members)

@app.route("/api/group-availability")
def get_group_availability():
    """Get availability details for members of a group"""

    members = crud.show_group_members(session["current_group_id"])
    availabilities = crud.create_availability_ref(session["current_group_id"])
    events = []

    for weekday in availabilities:
        attendees, start_time, end_time = crud.get_time_range_loop(availabilities, weekday)
        best_start, best_end = crud.get_best_range(availabilities, weekday, start_time, end_time)

        attendee_str = ""
        for attendee in attendees:
            if attendee_str:
                attendee_str = attendee_str + ", " + attendee
            else:
                attendee_str = attendee

        color = f"rgb(192, 225, 234, {len(attendees)/len(members)})"

        events.append({
            "id": weekday,
            "daysOfWeek": [weekday_dict[weekday]],
            "startTime": best_start.isoformat(),
            "endTime": best_end.isoformat(),
            "startRecur": datetime.now(),
            "title": f"{len(attendees)}: {attendee_str}",
            "display": "auto",
            "color": f"{color}",
            "textColor": "black",
            "borderColor": "black"
        })

    session.pop("current_group_id", default=None)

    return jsonify(events)

@app.route("/create-group")
def create_group():
    """Show form for creating a new group"""
    current_user_id = session.get("user_id")
    
    if not current_user_id:
        flash("You must be logged in to create a group.")
        return redirect("/")
    
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
    
    for user in new_group.users:
        notification = crud.add_notification(user_id = user.user_id,
                                             group_id = group_id,
                                             message = f"You have been added to {new_group.name}.",
                                             read_status=False)
        db.session.add(notification)
        db.session.commit()

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
    target_group = crud.get_group_by_id(group_id)

    if new_member in group_members:
        flash("Member already in group.")
    elif new_member in all_users:
        crud.add_user(user_email, group_id)
        crud.add_notification(new_member.user_id,
                              group_id=group_id,
                              message=f"You have been added to {target_group.name}.",
                              read_status=False)
        flash("New member added successfully.")
    else:
        flash("User not found. Please make sure to enter a valid email address.")

    return redirect(f"/groups/{group_id}")

@app.route("/group-pic-data", methods=["POST"])
def get_group_pic_data():
    """Use Cloudinary API to get group picture"""

    current_group_id = request.form.get("group-id")
    current_group = crud.get_group_by_id(current_group_id)
    group_pic = request.files['group-pic']

    result = cloudinary.uploader.upload(group_pic,
                                        api_key=CLOUDINARY_KEY,
                                        api_secret=CLOUDINARY_SECRET,
                                        cloud_name=CLOUD_NAME)

    img_url = result['secure_url']

    current_group.group_img = img_url
    db.session.commit()

    return redirect(f"/groups/{current_group_id}")

@app.route("/availability")
def view_availability():
    """View Availability"""

    logged_in_email = session.get("logged_in_email")
    current_user_id = session.get("user_id")

    if logged_in_email is None:
        flash("You must log in to view availability.")
        return redirect("/")
    else:
        current_user = crud.get_user_by_id(current_user_id)
        availabilities = current_user.availabilities
        return render_template("availability.html",
                               current_user=current_user,
                               availabilities=availabilities)

@app.route("/user-availability")
def get_availability():
    """Send current user's availability"""

    current_user_id = session.get("user_id")
    current_user = crud.get_user_by_id(current_user_id)

    availabilities = []

    for record in current_user.availabilities:
        new_record = {
            "avail_id": record.avail_id,
            "weekday": record.weekday,
            "start_time": record.start.strftime("%-I:%M %p"),
            "end_time": record.end.strftime("%-I:%M %p"),
        }
        availabilities.append(new_record)

    return jsonify(availabilities)

@app.route("/add-availability", methods=["POST"])
def add_availability():
    """Add a new availability record"""

    current_user_id = session.get("user_id")
    current_user = crud.get_user_by_id(current_user_id)
    weekday = request.json.get("weekday").title()
    weekday_as_int = weekday_dict[weekday]
    start = request.json.get("start_time")
    end = request.json.get("end_time")

    new_avail = crud.add_availability(current_user, weekday, weekday_as_int, start, end)
    db.session.add(new_avail)
    db.session.commit()

    new_record = {
        "weekday": weekday,
        "start_time": start,
        "end_time": end,
        "weekday_as_int": weekday_as_int,
        "avail_id": new_avail.avail_id
        }

    return jsonify({
        "success": True,
        "newRecord": new_record
    })

@app.route("/update-availability", methods=["POST"])
def update_availability():
    """Update a user's availability"""

    avail_id = request.json["availID"]
    new_weekday = request.json["weekday"].title()
    new_weekday_int = weekday_dict[new_weekday]
    new_start = request.json["startTime"]
    new_end = request.json["endTime"]

    crud.update_availability(avail_id, new_weekday, new_weekday_int, new_start, new_end)

    return {
        "success": True,
        "status": "You have updated your availability.",
        "redirect": "/availability",
        "weekday": f"{new_weekday}",
        "startTime": f"{new_start}",
        "endTime": f"{new_end}"
    }

@app.route("/delete-availability", methods=["POST"])
def delete_availability():
    """Delete a user's availability"""

    avail_id = request.json["availID"]
    target_avail = crud.get_availability_by_id(avail_id)
    weekday = target_avail.weekday
    crud.delete_availability(avail_id)

    return {
        "success": True,
        "status": f"You have deleted your availability record for {weekday}.",
        "redirect": "/dashboard",
        "target_avail": avail_id
    }

@app.route("/api/user-availability")
def get_user_availability():
    """Get availability details for logged in user"""

    user = crud.get_user_by_id(session["user_id"])

    events = []
    for availability in user.availabilities:
        events.append({
            "id": availability.avail_id,
            "daysOfWeek": [availability.weekday_as_int],
            "startTime": availability.start.isoformat(),
            "endTime": availability.end.isoformat(),
            "startRecur": datetime.now(),
            "title": availability.weekday,
            "display": "auto",
            "color": '#C0E1EA',
            "textColor": '#000000'
        })

    return jsonify(events)

@app.route("/search")
def show_search_form():
    """Display form for making searches"""

    return render_template("search_form.html")

@app.route("/api/search")
def search_for_activities():
    """Make API call to Google Places"""

    search_input = request.args.get('keyword', '')
    #get location from the form
    location = request.args.get('location', '')
    #use geocoding to convert location to latlng
    #should be able to pass in address and api key and the request will automatically format
    geo_location_results = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={API_KEY}")

    geo_results_dict = json.loads(geo_location_results.text)

    geo_location_lat = geo_results_dict['results'][0]['geometry']['location']['lat']
    geo_location_lng = geo_results_dict['results'][0]['geometry']['location']['lng']

    geo_location = f"{geo_location_lat}, {geo_location_lng}"

    #radius is in m and automatically clamped to max 50000m
    radius = request.args.get('radius', '50000')

    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'

    payload = {'key': API_KEY, 'keyword': search_input, 'location': geo_location, 'radius': radius}

    results = requests.get(url, payload)
    search_results_dict = json.loads(results.text)
    #will return an array of places called results

    return jsonify({"geo_location_lat": geo_location_lat,
                    "geo_location_lng": geo_location_lng,
                    "results": search_results_dict['results']})

@app.route("/settings")
def user_settings():
    """Display form that allows a user to change account settings"""

    current_user = crud.get_user_by_id(session["user_id"])

    return render_template("settings.html",
                           current_user=current_user)

@app.route("/user-changes", methods=["POST"])
def make_user_account_changes():
    """Make changes to user account"""

    current_user = crud.get_user_by_id(session["user_id"])

    old_password = request.form.get("old-password")
    new_pass_1 = request.form.get("new-pass-1")
    new_pass_2 = request.form.get("new-pass-2")

    if argon2.verify(old_password, current_user.password) and new_pass_1 == new_pass_2:
        current_user.password = crud.hash_password(new_pass_1)
        db.session.commit()
        flash("Password changed successfully.")

    elif new_pass_1 != new_pass_2:
        flash("New passwords don't match, please try again.")
        return redirect("/settings")

    elif not argon2.verify(old_password, current_user.password):
        flash("Incorrect password, please try again.")
        return redirect("/settings")

    return redirect("/settings")

@app.route("/user-pic-data", methods=["POST"])
def get_user_pic_data():
    """Use Cloudinary API to get user profile picture"""

    current_user = crud.get_user_by_id(session["user_id"])
    user_pic = request.files['user-pic']

    result = cloudinary.uploader.upload(user_pic,
                                        api_key=CLOUDINARY_KEY,
                                        api_secret=CLOUDINARY_SECRET,
                                        cloud_name=CLOUD_NAME)

    img_url = result['secure_url']

    current_user.user_img = img_url
    db.session.commit()

    return redirect("/settings")

@app.route("/about")
def about():
    """Display information about the app"""

    return render_template("about_us.html")

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
