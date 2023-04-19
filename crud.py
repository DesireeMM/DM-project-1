"""CRUD operations"""

from model import db, User, Event, Group, Availability, UserGroup, UserEvent, connect_to_db

#creation functions
def create_user(fname, lname, email, password, phone=None):
    """Create and return a new user"""

    user = User(fname=fname, lname=lname, email=email, phone=phone, password=password)

    return user

def create_event(created_by, group_id, name, datetime=None, activity=None, description=None):
    """Create and return a new event"""

    event = Event(created_by=created_by, group_id=group_id, name=name, datetime=datetime, activity=activity, description=description)

    return event

def create_group(created_by, name):
    """Create and return a new group"""

    group = Group(created_by=created_by, name=name)

    return group

def add_availability(user, weekday, start, end):
    """Create and return an availability record"""

    availability = Availability(user=user, weekday=weekday, start=start, end=end)

    return availability

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

#updating functions
def update_event(event_id, datetime, activity, description=None):
    """Update an event given its id"""

    target_event = Event.query.get(event_id)
    target_event.datetime = datetime
    target_event.activity = activity
    target_event.description = description
    db.session.commit()

def update_availability(avail_id, start, end):
    """Update a user's availability given their id"""

    target_user_avail = Availability.query.get(avail_id)
    target_user_avail.start = start
    target_user_avail.end = end
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