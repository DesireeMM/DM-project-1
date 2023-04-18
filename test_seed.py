"""Script to seed database"""

import os
import json
from random import choice, randint
from datetime import datetime

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
    password = 'test'

    new_user = crud.create_user(fname, lname, email, password)
    model.db.session.add(new_user)
model.db.session.commit()

#create some groups
group1 = crud.create_group(1, "Test_Group_1")
group2 = crud.create_group(2, "Test_Group_2")

model.db.session.add_all([group1, group2])
model.db.session.commit()



#create some events
event1 = crud.create_event(1, 1, "Test_Event_1")
event2 = crud.create_event(2, 2, "Test_Event_2")
event3 = crud.create_event(5, 2, "Test_Event_3")

model.db.session.add_all([event1, event2, event3])
model.db.session.commit()


#assign users to their groups
all_users = crud.get_users()

for user in all_users:
    if user.user_id <= 5:
        crud.add_user(user.email, 1)
    else:
        crud.add_user(user.email, 2)

#assign events to test users
for user in all_users:
    if 1 in user.groups:
        crud.add_event(user.email, 1)
    else:
        crud.add_event(user.email, 2)
        crud.add_event(user.email, 3)
