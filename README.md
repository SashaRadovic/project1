# Project 1

Web Programming with Python and JavaScript
1. File import-books-heroku.py is made to create table books in heroku db with columns isbn, title, author and year, corespodent with columns in books.csv and import data from books.csv into books table on heroku.
2. Database has two more tables - users, with id,  username, email, password, image_file columns and - posts, with post_id, headline, content,date_posted, rate, books_id(foreign key), id(foreign key coresponding users.id) columns.
3. Project file contains application.py and forms.py, templates and static folders, procfile, readme and requirements. Templates folder has 9 html pages that inherit from layout.html. Static foldes has book_pics and profile_pics folders and main.css file.
4. Forms.py contains  wtf-forms classes RegistrationForm, LoginForm, UpdateAccountForm, PostForm and SearchBookForm.
5. Application.py contains routes for html pages with db.execute SQL statements   
 