"""Models for my project."""

from flask_sqlalchemy import SQLAlchemy

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

    #establish relationships between users and events, users and groups
    events = db.relationship("Event", secondary="users_events", order_by="Event.datetime", back_populates="users")
    groups = db.relationship("Group", secondary="users_groups", back_populates="users")

    #establish relationship between user and their availability
    availabilities = db.relationship("Availability", order_by="Availability.weekday", back_populates="user")

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
    event_id = db.Column(db.Integer, db.ForeignKey("events.event_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
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
