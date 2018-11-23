# Access Control v3

This is the 3rd version the access control system that was devloped and iplemented at and for Rose State College.

This version includes some major updates, along with more security features.

### Updates
- Added web front end will ssl
- Improved back end door control
- Added more logging implmentations
- Completly re designed the backend code 

## Front end technlogy
The front end is all handled with flask. There is a login page for administrators. The website is able to handle multiple sessions, and has the functionality to track the IP addresses of whoever logs in.

## Back end technology
The back end was re designed and streamlined compared to its last iteration. Hardwarecontrol.py handles all of the door/LED/bepper controls. 

## SQL implmentation
Both the front end and the back end store information within databases. This is done with sqlalchemy. The one databse stores all the user who can access the door, all the users who can access the admin page of the web front end (these passwords are salted and hashed), the log of who accesses the door and website, along with all the actions of the admins while they are logged into the admin page.

## Authors
Ethan Fowler (C0ntra99), Jarris White