"""CRUD operations"""

from model import (db,
                   User,
                   Event,
                   Group,
                   Availability,
                   Notification,
                   UserGroup,
                   UserEvent,
                   connect_to_db)
from datetime import timedelta, datetime, date

weekday_dict = {"Sunday": 0,
                "Monday": 1,
                "Tuesday": 2,
                "Wednesday": 3,
                "Thursday": 4,
                "Friday": 5,
                "Saturday": 6}

#creation functions
def create_user(fname, lname, email, password, phone=None, user_img=None):
    """Create and return a new user"""

    user = User(fname=fname, lname=lname, email=email, phone=phone, password=password, user_img=user_img)

    return user

def create_event(created_by, group_id, name, datetime=None, activity=None, description=None):
    """Create and return a new event"""

    event = Event(created_by=created_by,
                  group_id=group_id,
                  name=name,
                  datetime=datetime,
                  activity=activity,
                  description=description)

    return event

def create_group(created_by, name):
    """Create and return a new group"""

    group = Group(created_by=created_by, name=name)

    return group

def add_availability(user, weekday, weekday_as_int, start, end):
    """Create and return an availability record"""

    availability = Availability(user=user, weekday=weekday, weekday_as_int=weekday_as_int, start=start, end=end)

    return availability

def add_notification(event_id, user_id, message, read_status=False):
    """Create and return a notification record"""

    notification = Notification(event_id=event_id, user_id=user_id, message=message, read_status=read_status)

    return notification

#querying functions for users
def get_users():
    """Return a list of all users in the database"""

    return User.query.all()

def get_user_by_id(user_id):
    """Return a user given their id"""

    return User.query.get(user_id)

def get_user_by_email(email):
    """Return a user given their email"""

    return User.query.filter(User.email == email).first()

#querying functions for events
def get_events():
    """Return a list of all events in the database"""

    return Event.query.all()

def get_event_by_id(event_id):
    """Return an event given its id"""

    return Event.query.filter(Event.event_id == event_id).first()

def get_event_by_name(name):
    """Return an event given its name"""
    #this may be useful if users want to search for certain event details later

    return Event.query.filter(Event.name == name).first()

def show_user_events(user_id):
    """Return a list of events for a user, given their id"""

    user = get_user_by_id(user_id)

    return user.events

def show_hosted_events(user_id):
    """Return a list of events hosted by a user, given their user_id"""

    return Event.query.filter(Event.created_by == user_id).all()

#querying functions for groups
def get_groups():
    """Return a list of all groups in the database"""

    return Group.query.all()

def get_group_by_id(group_id):
    """Return a group given its id"""

    return Group.query.filter(Group.group_id == group_id).first()

def get_group_by_name(name):
    """Return a group given its name"""
    #this may be useful if users want to search for certain groups

    return Group.query.filter(Group.name == name).first()

def show_user_groups(user_id):
    """Return a list of user's groups given their user_id"""

    user = get_user_by_id(user_id)

    return user.groups

def show_group_members(group_id):
    """Return a list of a group's members given its group_id"""

    group = get_group_by_id(group_id)
    members = group.users

    return members

#querying functions for availability
#revisit after exploring how calendar will display
def show_availability(user_id):
    """Return a list of a user's availabilities given their user_id"""

    user = User.query.get(user_id)
    return user.availabilities

    # return Availability.query.filter(Availability.user_id == user_id).all()
def get_availability_by_id(avail_id):
    """Return a specific availability record"""

    avail = Availability.query.get(avail_id)

    return avail

#updating functions
def update_event(event_id, name, datetime, activity, description=None):
    """Update an event given its id"""

    target_event = Event.query.get(event_id)
    target_event.name = name
    target_event.datetime = datetime
    target_event.activity = activity
    target_event.description = description
    db.session.commit()

def update_availability(avail_id, weekday, weekday_as_int, start, end):
    """Update a user's availability given their id"""

    target_user_avail = Availability.query.get(avail_id)
    target_user_avail.weekday = weekday
    target_user_avail.weekday_as_int = weekday_as_int
    target_user_avail.start = start
    target_user_avail.end = end
    db.session.commit()

def delete_availability(avail_id):
    """Delete a user's availability record given its id"""

    target_user_avail = Availability.query.get(avail_id)
    db.session.delete(target_user_avail)
    db.session.commit()

def delete_group(group_id):
    """Delete an entire group given its id"""
    print(group_id)
    target_group = Group.query.get(group_id)
    db.session.delete(target_group)
    db.session.commit()

def delete_event(event_id):
    """Delete an entire event given its id"""

    target_event = Event.query.get(event_id)
    db.session.delete(target_event)
    db.session.commit()

def update_user_groups(user_id, group_id):
    """Remove association between a user and a particular group."""

    target_user = User.query.get(user_id)
    target_group = Group.query.get(group_id)

    user_groups = target_user.groups
    user_groups.remove(target_group)

    db.session.commit()

def update_user_events(user_id, event_id):
    """Remove association between a user and a particular event."""

    target_user = User.query.get(user_id)
    target_event = Event.query.get(event_id)

    user_events = target_user.events
    user_events.remove(target_event)

    db.session.commit()

#relationship functions
def add_user(email, group_id):
    """Add a user to a group"""

    user = get_user_by_email(email)
    group = get_group_by_id(group_id)

    user.groups.append(group)
    db.session.commit()

def add_event(email, event_id):
    """Add an event to a group"""

    user = get_user_by_email(email)
    event = get_event_by_id(event_id)

    user.events.append(event)
    db.session.commit()

#main availability calculator functions
def create_availability_ref(group_id):
    """Create a dictionary to hold availabilities of group members given the group id"""

    #first, get all group members
    all_members = show_group_members(group_id)

    #make a dictionary for member availabilities:
    availabilities = {}

    #loop through members to populate dictionary
    for member in all_members:
        for availability in member.availabilities:
            if availability.weekday not in availabilities:
                availabilities[availability.weekday] = {member.fname: (availability.start, availability.end)}
            else:
                availabilities[availability.weekday].update({member.fname:(availability.start, availability.end)})

    #at this point i have a dictionary
    #dictionary has the days of the week containing another dictionary
    #nested dictionary has key = member name and value = start and end times as a tuple
    return availabilities

#need to find best day and time
def get_best_weekday(availabilities):
    """Return the weekday that has the most members available"""
    longest_so_far = None
    for key, value in availabilities.items():
        if longest_so_far is None or len(value) > longest_so_far:
            longest_so_far = len(value)
            best_weekday = key
    
    return best_weekday

def get_time_range_loop(availabilities, weekday):
    """Given the day of the week, find the earliest start time and latest end time.
    We need these times for our for loop determining best time range."""

    records = availabilities[weekday]

    attendees = records.keys()

    poss_start_times = []
    poss_end_times = []

    for record in records.values():
        poss_start_times.append(record[0])
        poss_end_times.append(record[1])

    start_time = min(poss_start_times)
    end_time = max(poss_end_times)

    return attendees, start_time, end_time
#now we have a list of possible attendees, the earliest possible start time, and the latest possible end time

def add_time(time1, delta):
    """Function used to convert a time object to a datetime object.
    Necessary to add a time object and a timedelta object."""
    
    new_dt = datetime.combine(date.today(), time1) + delta
    return new_dt.time()

def get_best_range(availabilities, weekday, start_time, end_time):
    """Given a dictionary of availabilities, return a time range where most people are available"""
    records = availabilities[weekday]

    #create an empty dictionary to hold times:number of people available
    time_range_dict = {}
    #we'll want to loop through in 30 min increments
    interval = timedelta(minutes=30)
    loop_start_time = start_time

    #starting from the earliest start time and going to the latest end time
    while loop_start_time < end_time:
    #for each of those times, determine how many people are available at those times
        for times in records.values():
            if times[0] <= loop_start_time <= times[1]:
                #add a key:value pair to the dictionary
                time_range_dict[loop_start_time] = time_range_dict.get(loop_start_time, 0) + 1
            else:
                continue
        loop_start_time = add_time(loop_start_time, interval)
#now we have a dictionary where keys are the 30-min interval times and values are the number of people available
#then we can get the max of the values
    max_people = max(time_range_dict.values())
#loop through key:value pairs
    ideal_range = []
#until you find the max value -- this will be beginning of ideal range
    for key, value in time_range_dict.items():
        if value == max_people:
            ideal_range.append(key)
        else:
            continue
#keep going as long as you see that max value
    best_start_time = min(ideal_range)
    best_end_time = max(ideal_range)

    return best_start_time, best_end_time


if __name__ == "__main__":
    from server import app
    connect_to_db(app)



#write a function to pull out the values from a datetime
# %a for Weekday, short version
# %A Weekday, full version
# %h hour 00-12
# %M minute
# %S second
# %p AM/PM
