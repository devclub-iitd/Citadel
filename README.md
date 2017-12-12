# Bookshelf


## What is it all about?
We bring to you one of its kind crowd contributed portal. 
For the students, by the students and of the students. 
It acts as a one stop platform for all the learning that you will need.
Share, learn and go.
Currently the workpattern is this, people contibute using the upload button, this dumps the file in media/unapproved.
Using the approve page authorised people can add the papers.


## Getting Started: 
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

The following packages are required on a linux machine to compile and use the software package.

```
python3
pip3
```

### Dependencies
```
course.json --> File that lists all the courses
profs.json --> File that maps uids of Profs to their Names
```

### Installing

Deploying bookShelf is fairly simple. Just issue the following commands on a linux machine

```
git clone https://github.com/devclub-iitd/bookShelf.git
cd bookShelf
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
mkdir media
mkdir media/database
mkdir media/unapproved
cd make_folder
python make_folder.py
mv DATA/* ../media/database/
cd bookShelf
python manage.py migrate
python manage.py createsuperuser (Create a super user by following the instructions)
deactivate
```
### Running the Web-App


You can run the code using the command:

```
cd bookShelf
source venv/bin/activate
cd bookShelf
python manage.py runserver
``` 

Thereafter, go to the home page at `localhost:8000`

For admin page go to `localhost:8000/admin/`


## Built With

* [Python 3.6](http://www.python.org/) - Python is a programming language that lets you work quickly and integrate systems more effectively.
* [Django 1.11.1](https://www.djangoproject.com/) - The web framework for perfectionists with deadlines.


## IMPORTANT NOTE
Before making ANY CHANGE in the REPO:  
**Make sure to commit changes from the VM and then make any changes. And after making any changes on your local machine, please commit the changes and pull them in the VM.**


## How to approve and disapprove requests?
Go to ``/books/approve`` and accept or reject or rename each request

PS: You must be logged in to do that ;)  

## Tracking: 

Tracking and Page hits are currently implemented in two ways:

1. Google Analytics - Currently, Google analytics is operational for **www.cse.iitd.ac.in/devclub/studyportal**
2. Admin Panel - Course Page hits can also be found from the admin panel. Go to the requisite course code and check the pagehits field

## API

```
* /books/api/structure/ : would return the whole directory structure
```



						
