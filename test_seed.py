"""Script to seed database"""

import os
import json
from random import choice, randint
from datetime import datetime, time

import crud
import model
import server

os.system("dropdb project_db")
os.system("createdb project_db")

model.connect_to_db(server.app)
model.db.create_all()

#create some users
for n in range(10):
    fname = f'Tester{n}'
    lname = f'McTester{n}'
    email = f'user{n}@test.com'
    password = crud.hash_password('test')

    new_user = crud.create_user(fname, lname, email, password)
    model.db.session.add(new_user)

#creating users for demo video
password = crud.hash_password('test')
goose = crud.create_user("Goose", "Lim", "goose_lim@test.com", password)
pablo = crud.create_user("Pablo", "Wang", "pablo_wang@test.com", password)
mocha = crud.create_user("Mocha", "Lee", "mocha_lee@test.com", password)
arthur = crud.create_user("Arthur", "Morgan", "arthur_morgan@test.com", password)
jojimon = crud.create_user("Joji", "Mon", "jojimon@test.com", password)
moody = crud.create_user("Moody", "Girl", "moodygirl@test.com", password)
two = crud.create_user("Two", "PointOh", "twopointoh@test.com", password)
model.db.session.add_all([goose, pablo, mocha, arthur, jojimon, moody, two])
model.db.session.commit()

#create some groups
group1 = crud.create_group(1, "Test_Group_1")
group2 = crud.create_group(2, "Test_Group_2")
group3 = crud.create_group(5, "Test_Group_3")

model.db.session.add_all([group1, group2, group3])
model.db.session.commit()



#create some events
event1 = crud.create_event(1, 1, "Test_Event_1")
event2 = crud.create_event(2, 2, "Test_Event_2")
event3 = crud.create_event(5, 2, "Test_Event_3")
event4 = crud.create_event(5, 3, "Test_Event_4")

model.db.session.add_all([event1, event2, event3, event4])
model.db.session.commit()


# #assign users to their groups
all_users = crud.get_users()

# for user in all_users:
#     if user.user_id <= 5:
#         crud.add_user(user.email, 1)
#     if user.user_id > 5:
#         crud.add_user(user.email, 2)
#     if 3 < user.user_id <= 8:
#         crud.add_user(user.email, 3)

# #assign events to test users
# for user in all_users:
#     for group in user.groups:
#         if group.group_id == 1:
#             crud.add_event(user.email, 1)
#         if group.group_id == 2:
#             crud.add_event(user.email, 2)
#             crud.add_event(user.email, 3)
#         if group.group_id == 3:
#             crud.add_event(user.email, 4)

#adding availabilities
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

weekday_dict = {"Sunday": 0,
                "Monday": 1,
                "Tuesday": 2,
                "Wednesday": 3,
                "Thursday": 4,
                "Friday": 5,
                "Saturday": 6}

five_pm = time(17, 00)
ten_pm = time(22, 00)
six_pm = time(18, 00)
nine30_pm = time(21, 30)
noon = time(12, 00)
nine_am = time(9, 00)
four_pm = time(16, 00)
eleven30_am = time(11, 30)

start_times = [nine_am, eleven30_am, noon, four_pm]
end_times = [five_pm, six_pm, nine30_pm, ten_pm]

i = 0
while i < 3:
    for user in all_users:
        weekday=choice(weekdays)
        new_avail =crud.add_availability(user=user, weekday=weekday, weekday_as_int=weekday_dict[weekday], start=choice(start_times), end=choice(end_times))
        model.db.session.add(new_avail)
        model.db.session.commit()
    i += 1