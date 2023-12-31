## Overview
This app uses Flask and SQlite to manage a zoo database with a secure login requirement feature and a bootstrap layout.  
  
Install requirements.txt and run app.py (or start flask with flask run)  
  
## Features
Manage a Zoo Database (SQLite & JSON)
* CRUD
* Add
* Edit (takes existing credentials to another page to edit)
* Delete 
* Default image icon display in the Image column (if none was given) 
* Diet category (Predator/Herbivore)  
  
Login and Register (SQlite & JSON)
* Login
* Register (to a separate user database with an encrypted hashed password)
* Login requirement for access to the rest of the website
* Flask Flash messages for errors
* Replaces both Login and Register buttons with a Logout button after logging in



