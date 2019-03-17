import os
import requests
import gunicorn
import secrets, datetime
from flask import Flask, session, render_template, url_for, flash, redirect, request, abort, jsonify
from PIL import Image
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, SearchBookForm
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, UserMixin, current_user, logout_user, login_required
from flask_wtf import FlaskForm
#postgresql://postgres:123@localhost:5432/project1
os.environ["DATABASE_URL"]="postgres://yxhgpatjczqebb:7b840aada0efcb2afc3b315236a7753c7a5537772fbfc3451bea67f53d9e825e@ec2-50-19-109-120.compute-1.amazonaws.com:5432/d8v6ci2dq60tlp"
app = Flask(__name__)
app.config['SECRET_KEY'] = '101df5a0682cd99e66d32f2adbae1df5'
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category ="info"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
bcrypt=Bcrypt(app)


class User(UserMixin):
    def __init__(self ,  id ,  active=True):

        self.id = id

        self.username =username = db.execute("SELECT username FROM users WHERE id =:id", {"id":id}).fetchone()[0]
        self.email =email = db.execute("SELECT email FROM users WHERE id =:id", {"id":id}).fetchone()[0]
        self.image_file =image_file = db.execute("SELECT image_file FROM users WHERE id =:id", {"id":id}).fetchone()[0]
        self.active = active







@app.route("/")
@app.route("/index")
def index():

    posts = db.execute(
    "SELECT headline, content, username, title, image_file, date_posted, post_id, posts.books_id, rate FROM posts INNER JOIN books ON posts.books_id = books.books_id INNER JOIN users ON posts.id = users.id "
    ).fetchall()

    books =db.execute("SELECT DISTINCT title, author,isbn,year, books.books_id FROM books INNER JOIN posts ON books.books_id=posts.books_id ").fetchall()




    return render_template("index.html", posts=posts, books=books)


@app.route("/about")
def about():
    return render_template("about.html")



@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'), code=302, Response=None)
    form = RegistrationForm()


    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        db.execute("INSERT INTO users (username, email, password, image_file) VALUES (:username, :email, :password, :image_file)",
                   {"username": form.username.data, "email": form.email.data, "password": hashed_password, "image_file":"default.jpg"})
        db.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title ='Register', form =form)





@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('book_search'))
    form = LoginForm()

    if form.validate_on_submit():
        password =db.execute("SELECT password FROM users WHERE email=:email",{"email": form.email.data} ).fetchone()
        useremail = db.execute("SELECT email FROM users WHERE email=:email", {"email":form.email.data}).fetchone()
        if useremail and bcrypt.check_password_hash(password[0],form.password.data ) :
            id  = int(db.execute("SELECT id FROM users WHERE email=:email", {"email":form.email.data}).fetchone()[0])
            user =User(id)

            login_user(user, remember=form.remember.data, duration=None, force=True, fresh=True)
            next_page = request.args.get('next', 'book_search')
            return redirect(next_page) if next_page else redirect(url_for('book_search'), code=302, Response=None)
        else:
            flash('Please check your email or password', 'danger')
    return render_template('login.html', title ='Login', form =form)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)



    return picture_fn



@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit() :
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data


        db.execute("UPDATE users SET username=:username WHERE id=:id",{"id": current_user.id,"username":current_user.username})
        db.execute("UPDATE users SET email=:email WHERE id=:id",{"id": current_user.id,"email":current_user.email})
        db.execute("UPDATE users SET image_file=:image_file WHERE id=:id",{"id": current_user.id,"image_file":current_user.image_file})


        db.commit()

        flash('Your account has been updated!', category='success')
        return redirect(url_for('account'), code=302, Response=None)
    elif request.method == 'GET':

         form.username.data =current_user.username
         form.email.data =current_user.email

    image_file = url_for('static', filename ='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form = form)





@login_manager.user_loader
def load_user(id):

    return User(id)

@app.route("/post/new/<int:books_id>",  methods=['GET', 'POST'])
@login_required

def new_post(books_id):

    form = PostForm()
    book =db.execute("SELECT * FROM books WHERE books_id=:books_id", {"books_id":books_id}).fetchone()
    post =db.execute("SELECT posts.post_id FROM posts WHERE posts.books_id=:books_id AND posts.id=:current_user",{"books_id":books_id, "current_user":current_user.id}).fetchone()

    if post != None:
        flash('You have already posted a review for this book!', category='danger')
        return redirect(url_for('update_post', post_id=post.post_id), code=302, Response=None)
    elif form.validate_on_submit() :




        db.execute(
        "INSERT INTO posts (headline, content, books_id, id, rate) VALUES (:headline, :content, :books_id, :id, :rate)", {"headline": form.title.data, "content": form.content.data, "books_id": books_id, "id": current_user.id, "rate":form.rate.data}
            )
        db.commit()
        flash('Your post has been created!', category='success')
        return redirect(url_for('book_select', books_id=books_id), code=302, Response=None)
    return render_template('create_post.html', title ='Book review ', form = form, legend ='Book review', books_id=books_id, book=book, post=post)

@app.route("/post/<int:post_id>")
def post(post_id):

    post = db.execute(
        "SELECT headline, content, username, title, image_file, date_posted, post_id, rate from users INNER JOIN posts ON posts.id = users.id   INNER JOIN books ON posts.books_id= books.books_id WHERE posts.post_id = :post_id ",{"post_id": post_id}
    ).fetchone()




    return render_template('post.html', title = post.headline, post=post)


@app.route("/book_select/<int:books_id>")
def book_select(books_id):

    posts = db.execute(
    "SELECT headline, content, username, title, image_file, date_posted, post_id, posts.books_id, rate FROM posts INNER JOIN books ON posts.books_id = books.books_id INNER JOIN users ON posts.id = users.id "
    ).fetchall()

    book =db.execute("SELECT  title, author,isbn,year, books.books_id FROM books WHERE books.books_id=:books_id ",{"books_id":books_id}).fetchone()

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "07laCG3u6fW0ICHFIKUVOQ", "isbns":  book.isbn})
    data = res.json()



    return render_template('book_select.html', books_id=books_id, posts=posts, book=book, data=data)




@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):

    post = db.execute(
        "SELECT headline, content, username, title, image_file, date_posted, post_id, rate,posts.books_id from users INNER JOIN posts ON posts.id = users.id   INNER JOIN books ON posts.books_id= books.books_id WHERE posts.post_id = :post_id ",{"post_id": post_id}
    ).fetchone()

    book =db.execute("SELECT * FROM books WHERE books_id=:books_id", {"books_id":post.books_id}).fetchone()

    if post.username != current_user.username:
        abort(403, "You can't change the post from different user" )
    form =PostForm()
    #logic for update post headline and content
    if form.validate_on_submit():
    #creating variables out of form inputs
        post_headline = form.title.data
        post_content = form.content.data
        post_rate = form.rate.data
    #SQL statements for updating post
        db.execute("UPDATE posts SET rate=:rate WHERE post_id=:post_id",{"post_id": post_id,"rate":post_rate})
        db.execute("UPDATE posts SET headline=:headline WHERE post_id=:post_id",{"post_id": post_id,"headline":post_headline})
        db.execute("UPDATE posts SET content=:content WHERE post_id=:post_id",{"post_id": post_id,"content":post_content})
        db.execute("UPDATE posts SET date_posted=:date_posted WHERE post_id=:post_id",{"post_id": post_id,"content":post_content, "date_posted":datetime.datetime.now().strftime('%Y-%m-%d')})
        db.commit()
        flash('Your post has been updated!', category='success')
        return redirect(url_for('index'))
    #populating the form from existing database values
    elif request.method =="GET":
        form.title.data = post.headline
        form.content.data = post.content
        form.rate.choice = post.rate

    return render_template('create_post.html', title ='Update Post', form = form, book=book ,legend ='Update Post')




@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = db.execute(
        "SELECT headline, content, username, title, image_file, date_posted, post_id from users INNER JOIN posts ON posts.id = users.id   INNER JOIN books ON posts.books_id= books.books_id WHERE posts.post_id = :post_id ",{"post_id": post_id}
    ).fetchone()
    if post.username != current_user.username:
        abort(403)
    db.execute("DELETE FROM posts WHERE post_id = :post_id", {"post_id": post_id})
    db.commit()
    flash('Your post has been deleted!', category='success')
    return redirect(url_for('index'), code=302, Response=None)



@app.route("/book_search", methods=['POST', 'GET'])
@login_required
def book_search():

        form=SearchBookForm()


        choice =form.search_type.data

        query_string=form.query_input.data
        query_display_choices=[]

        if form.validate_on_submit():
            if choice=="isbn":
               query_display_choices=[(book.isbn,book.title, book.author, book.books_id, book.year) for book in db.execute("SELECT isbn, title, author, books_id, year FROM books WHERE isbn LIKE :query_string ", {"query_string":"%"+query_string+"%"}).fetchall()]
               if query_display_choices == []:
                   flash('Your query produced no results. Please, change your input and try again. ', category='danger')

            elif choice=="title":
               query_display_choices=[(book.isbn,book.title, book.author, book.books_id, book.year) for book in db.execute("SELECT isbn, title, author, books_id, year FROM books WHERE title LIKE :query_string", {"query_string":"%"+query_string+"%"}).fetchall()]

               if query_display_choices == []:
                   flash('Your query produced no results. Please, change your input and try again. ', category='danger')
            elif choice=="author":
               query_display_choices=[(book.isbn,book.title, book.author, book.books_id, book.year) for book in db.execute("SELECT isbn, title, author, books_id, year FROM books WHERE author LIKE :query_string ", {"query_string":"%"+query_string+"%"}).fetchall()]
               if query_display_choices == []:
                   flash('Your query produced no results. Please, change your input and try again. ', category='danger')



        return render_template('book_search.html',query_display_choices=query_display_choices,choice=choice, form = form, legend='Book Search')

@app.route("/api/<string:isbn>")
def api( isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    if book is None:
        return abort(404, "Wrong ISBN!")

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    rewiev_count=db.execute("SELECT COUNT(books_id) FROM posts WHERE books_id=:books_id",{"books_id":book.books_id}).fetchone()
    average_rating=db.execute("SELECT AVG(rate) FROM posts WHERE books_id=:books_id",{"books_id":book.books_id}).fetchone()

    return jsonify(
        title= book.title,
        author= book.author,
        year=book.year,
        isbn= book.isbn,
        review_count= rewiev_count[0],
        average_rating= str(average_rating[0])
    )


if __name__ == '__main__':
    app.run(debug= True)
