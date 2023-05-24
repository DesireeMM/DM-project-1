# When To Chill

Learn more about the developer on [LinkedIn](https://www.linkedin.com/in/desiree-morimoto-9470481b0/)

If you prefer, you can watch a brief demo video of my project here:  
   [![When To Chill Demo Link](http://img.youtube.com/vi/ZNINJhmmvRE/0.jpg)](http://www.youtube.com/watch?v=ZNINJhmmvRE)

## Table of Contents
- [Project Description](#overview)
- [Technologies Used](#technologiesused)
- [APIs Used](#apisused)
- [How To Use When To Chill](#howtoguide)

## Project Information

#### <a name="overview"></a>Description
"When to Chill" is a Flask-based web application that aims to make navigating adult friendships a little easier. The app allows friends to input their schedules and preferences, suggesting the best date and time to hang out based on their availability. Users can keep track of groups and events they are involved in and view them on a personal calendar, provided by fullcalendar.io's JavaScript API. An integration with Google Maps provides a search function to help give users ideas for activities. With "When to Chill," you can take the stress out of coordinating with friends and focus on creating memorable moments together.

#### <a name="technologiesused"></a>Technologies Used
- Python
- Flask
- HTML
- Jinja2
- JavaScript
- AJAX
- React
- CSS
- Bootstrap
- PostgreSQL
- SQLAlchemy
- passlib
- unittest

#### <a name="apisused"></a>APIs Used
- [Cloudinary API](https://cloudinary.com/documentation/cloudinary_references)
- [fullcalendar.io](https://fullcalendar.io/docs)
- [Google Maps API](https://developers.google.com/maps/documentation)
  * [Geocoding API](https://developers.google.com/maps/documentation/geocoding)
  * [Places API](https://developers.google.com/maps/documentation/places/web-service/search-nearby)
  * [Maps JavaScript API](https://developers.google.com/maps/documentation/javascript)

## <a name="howtoguide"></a>How To Use When To Chill
### Topics
- [Account](#account)
- [Availability Records](#availability)
- [Groups](#groups)
- [Events](#events)
- [Account Settings](#settings)

### <a name="account"></a>Create An Account/Logging In
Creating an account is simple. Enter in your email, first name, last name, and a password. If you'd like, you can opt to add a phone number.  
   If your email is already associated with an account, you won't be able to create a second one.  
>Password security is managed with argon2 hashing, but to protect yourself from security breaches, choose a password unique to this site.  

Once you've created an account, you'll be redirected back to the homepage to login.

If you already have an account, just enter in your account credentials to be taken to your user dashboard.

### <a name="availability"></a>Adding/Updating Availability Records
###### Adding
Select a day of the week, start of your availability block, and end of your availability block using the dropdown menus under **_Add New Availability Record_**  
> *Note: the app works best when your time blocks start and end on the hour or half hour.*

###### Updating
1. Click the **_Change Record_** button under the availability record you'd like to edit.
> Alternatively, you can delete the record entirely by clicking **_Delete Record_** and confirming your action.
2. Make changes using the dropdown menus that appear.
3. Click the **_Make Changes_** button to save your edits.

### <a name="groups"></a>Groups
###### Creating
1. Use the navbar to navigate to the form to create groups.
  * Click **_Groups_** in the navbar to show a dropdown menu where you can access **_Create New Group_**.
2. Add in a *Group Name* -- this is what will display on users' dashboards.
3. Click the **_Add Another Member_** button to display a field for other users' email addresses.
  * You can add members to a group later from the group's homepage instead.
4. Click the **_Create Group_** button when satisfied with the fields.
###### Updating
Newly created groups will show up on your dashboard or on your **_My Groups_** page.

For groups you have created, you have the option to:
  * Uploading a group photo
  * Adding New Members
  * Deleting the group entirely
###### What if I no longer want to be a part of a group?
If you need to leave a group, navigate to **_My Groups_** and hit the **_Leave Group_** button for the group wish to leave.

### <a name="events"></a>Events
###### Creating
1. Use the navbar to navigate to the form to create events.
  * Click **_Events_** in the navbar to show a dropdown menu where you can access **_Create New Event_**.
2. Select the group you are planning to invite from the dropdown menu.
3. Add in an *Event Name* -- this is what will display on users' personal events calendars.
4. *Description*, *Location*, *Date*, and *Time* are all optional here.
5. Click the **_Create Event_** button when satisfied with the fields.
###### Updating
Newly created events will show up on your dashboard or on your **_My Events_** page.

To update an event you are hosting:
1. Click the event you want to update.
2. Click the **_Update This Event_** button.
> Alternatively, you can delete the event entirely by clicking **_Delete Event_** and confirming your action.
3. Make any necessary edits to your event using the form fields.
> The best day and time for your group to hang out will be displayed here for reference.
> If you want to view the group's full availability, click **_View Full Availability_**.
4. Click the **_Make Changes_** button to save your edits.
###### What if I can't make an event?
If you can't make an event you've been invited to, simply click **_Cannot Attend_** from your **_My Events_** page.

### <a name="settings"></a>Managing Account Settings
###### Changing Your Password
You must enter your current password in order to change it to something else.  
   Please make sure your new password matches in both fields before clicking **_Change Password_**.