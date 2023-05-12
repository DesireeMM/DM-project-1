"""Models for my project."""

from flask_sqlalchemy import SQLAlchemy
from passlib.hash import argon2

db = SQLAlchemy()

#create my user class
class User(db.Model):
    """User on my app"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(12), nullable=True)
    password = db.Column(db.String(250), nullable=False)
    user_img = db.Column(db.String, nullable=True)

    #establish relationships between users and events, users and groups
    events = db.relationship("Event", secondary="users_events", order_by="Event.datetime", back_populates="users")
    groups = db.relationship("Group", secondary="users_groups", back_populates="users")

    #establish relationship between user and their availability
    availabilities = db.relationship("Availability", order_by="Availability.weekday_as_int", back_populates="user")

    #establish relationship between user and their event notifications
    notifications = db.relationship("Notification", back_populates="user")

    def __repr__(self):

        return f"<User user_id: {self.user_id} email: {self.email}>"

#create my event class
class Event(db.Model):
    """Event on my app"""

    __tablename__ = "events"

    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    group_id = db.Column(db.Integer, db.ForeignKey("groups.group_id"))
    name = db.Column(db.String(100), nullable=False)
    datetime = db.Column(db.DateTime, nullable=True)
    activity = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String, nullable=True)

    #establish relationships between users and events, events and a group
    users = db.relationship("User", secondary="users_events", back_populates="events")
    group = db.relationship("Group", back_populates="events")

    #establish relationship between an event and its notifications
    notification = db.relationship("Notification", back_populates="event")

    def __repr__(self):

        return f"<Event event_id: {self.event_id} name:{self.name}>"

#create my group class
class Group(db.Model):
    """Group on my app"""

    __tablename__ = "groups"

    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    name = db.Column(db.String(50), nullable=False)
    group_img = db.Column(db.String, nullable=True)

    #establish relationships between groups and events, groups and users
    events = db.relationship("Event", back_populates="group")
    users = db.relationship("User", secondary="users_groups", back_populates="groups")

    def __repr__(self):

        return f"<Group group_id: {self.group_id} name: {self.name}>"

#create availability class
class Availability(db.Model):
    """Contains information on user's availability"""

    __tablename__ = "availabilities"

    avail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    weekday = db.Column(db.String(15))
    weekday_as_int = db.Column(db.Integer)
    start = db.Column(db.Time, nullable=True)
    end = db.Column(db.Time, nullable=True)

    #establish relationship between users and their availability
    user = db.relationship("User", back_populates="availabilities")

    def __repr__(self):

        return f"<Availability id: {self.avail_id} user: {self.user_id}>"

#create notification class
class Notification(db.Model):
    """Contains notifications for users"""

    __tablename__ = "notifications"

    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.event_id"), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.group_id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    message = db.Column(db.String)
    read_status = db.Column(db.Boolean, default=False)

    #establish relationships between notifications and their event and user
    user = db.relationship("User", back_populates="notifications")
    event = db.relationship("Event", back_populates="notification")

    def __repr__(self):

        return f"<Notification id:{self.notification_id} event:{self.event.name}>"

#create UserGroup association table
class UserGroup(db.Model):
    """Association table for users and groups"""

    __tablename__ = "users_groups"

    usergroup_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    group_id = db.Column(db.Integer, db.ForeignKey("groups.group_id"))

    def __repr__(self):

        return f"<UserGroup id: {self.usergroup_id} user: {self.user_id} group: {self.group_id}>"

#create UserEvent association table
class UserEvent(db.Model):
    """Association table for users and events"""

    __tablename__ = "users_events"

    userevent_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.event_id"))

    def __repr__(self):

        return f"<UserEvent id: {self.userevent_id} user: {self.user_id} event: {self.event_id}"

def create_test_data():
    """Create sample data for testing database"""

    #add in sample data for users
    hashed_pw = argon2.hash("testing")
    
    user1 = User(fname="John", lname="Doe", email="john_doe@test.com", password=hashed_pw)
    user2 = User(fname="Jane", lname="Doe", email="jane_doe@test.com", password=hashed_pw)
    user3 = User(fname="Wade", lname="Watts", email="wade_watts@test.com", password=hashed_pw)
    user4 = User(fname="Helen", lname="Harris", email="helen_harris@test.com", password=hashed_pw)

    db.session.add_all([user1, user2, user3, user4])
    db.session.commit()

    #add in sample data for groups
    group1 = Group(created_by=1, name="Sixers")
    group2 = Group(created_by=3, name="Hunters")

    db.session.add_all([group1, group2])
    db.session.commit()

    #add in sample events
    event1 = Event(created_by=2, name="Job Fair")
    event2 = Event(created_by=3, name="Egg Hunt")

    db.session.add_all([event1, event2])
    db.session.commit()

    #add users to a group
    rel1 = UserGroup(user_id=1, group_id=1)
    rel2 = UserGroup(user_id=2, group_id=1)
    rel3 = UserGroup(user_id=3, group_id=2)
    rel4 = UserGroup(user_id=4, group_id=2)

    db.session.add_all([rel1, rel2, rel3, rel4])
    db.session.commit()

    #add users to an event
    rel5 = UserEvent(user_id=1, event_id=1)
    rel6 = UserEvent(user_id=2, event_id=1)
    rel7 = UserEvent(user_id=3, event_id=2)
    rel8 = UserEvent(user_id=4, event_id=2)

    db.session.add_all([rel5, rel6, rel7, rel8])
    db.session.commit()




def connect_to_db(flask_app, db_uri="postgresql:///project_db", echo=False):
    """Function to connect to my project database"""
    flask_app.config["SQLALCHEMY_DATABASE_URI"]= db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


if __name__ == "__main__":
    from server import app

    connect_to_db(app)
