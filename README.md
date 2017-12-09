# Bookshelf

## Getting Started: 
1. Install requirements.txt file and run server at your local device using pip install -r requirements.txt
2. Thereafter, go to the home page at localhost:<port_number>/books/
3. For admin page go to localhost:<port_number>/admin/

-------------------------------------------------------------------------------------------------------------------------------------------
## What is it all about?
We bring to you one of its kind crowd contributed portal. 

For the students, by the students and of the students. 

It acts as a one stop platform for all the learning that you will need.

Share, learn and go.

Currently the workpattern is this, people contibute using the upload button, this dumps the file in media/unapproved.

Using the approve page authorised people can add the papers.

### Technology used
We will work using python 3.6

and latest version of django that is django 1.11.1


### IMPORTANT NOTE
Before making ANY CHANGE in the REPO:  
**Make sure to commit changes from the vm and then make any changes. And after making any changes on your local machine, please commit the changes and pull them in the vm.**

superuser credentials
both username and password same as **youshouldknow**

-----------------------------------------------------------------------------------------
### How to approve and disapprove requests?
Go to /books/approve and accept or reject or rename each request
PS: You must be logged in to do that ;)  

Tracking: Tracking and Page hits are currently implemented in two ways:
1. Google Analytics - Currently, Google analytics is operational for **www.cse.iitd.ac.in/devclub/studyportal**
2. Admin Panel - Course Page hits can also be found from the admin panel. Go to the requisite course code and check the pagehits field :)
-----------------------------------------------------------------------------------------
### API

/books/api/structure/ : would return the whole directory structure

/books/api/upload : upload api. Please provide course_code (APL100), sem(1), year(2016-17), type_exam(minor1), other_text(<name of book>), professor(handle of professor), document(file)

# TODO List
1. Remove all the unnecessary light/dark thing
2. Format upload and login page nicely
3. Implement infinite horizontal scrolling to avoid page reload on navigation
4. More papers to be added soon.
# Bugs List
<empty>

						

