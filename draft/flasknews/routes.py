import os 
import secrets
from sqlalchemy import desc
from flask import render_template, url_for, flash, redirect, request, abort
from flasknews import app, db, bcrypt
from flasknews.forms import RegistrationForm, LoginForm, UpdateAccountForm, RegistrationFormReporter, ArticleForm
from flasknews.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

session = {}
# posts = [
#     {
#         'author': 'Trmúa Hmề',
#         'title': 'Article 1',
#         'content': 'Cách để trở thành Trmúa Hmề trong mắt người khác official',
#         'date_posted': 'April 20, 2021'
#     },
#     {
#         'author': 'Trmúa Hmề bủh',
#         'title': 'Article 2',
#         'content': 'Cách để trở thành Trmúa Hmề dảk',
#         'date_posted': 'April 20, 2021'
#     },
# ]

article_by_categories = []

@app.route("/")
@app.route("/home")
def home():
    # store previous page into session for auto redirect   
    session['url'] = url_for('home')

    # post query from database
    # posts = Post.query.all()
    posts = Post.query.order_by(desc(Post.date_posted)).all()
    latest = posts
    if posts:
        latest = posts[0]
        posts = posts[1:4]

    categories = ["Stars", 'TV Shows', "Music", "Sport", "Fashion", "Travel", "Life"]
    for cat in categories:
        query_articles = Post.query.filter_by(category = cat).order_by(desc(Post.date_posted)).all()
        if query_articles:
            temp = query_articles
        article_by_categories.append(temp)


    return render_template('home.html', posts = posts, latest = latest, article_by_categories = article_by_categories, categories = categories, len = len(categories))
@app.route("/about")
def about():
    # store previous page into session for auto redirect
    session['url'] = url_for('about')

    return render_template('about.html', title = 'About')

@app.route("/register", methods = ['GET', 'POST'])
def register():
    # user already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, 
                    email = form.email.data, 
                    password = hashed_password,
                    is_male = form.is_male.data, 
                    type_user = form.type_user,
                    description = form.description.data)
        
        # add to database
        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {form.username.data}!', 'success')

        # redirect user to login page
        return redirect(url_for('login'))

    return render_template('register.html', title = 'Register', form = form)


@app.route("/reg_reporter", methods = ['GET', 'POST'])
def register_reporter():
    # user already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationFormReporter()
    if form.validate_on_submit():
        # hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, 
                    email = form.email.data, 
                    password = hashed_password,
                    is_male = form.is_male.data, 
                    type_user = form.type_user,
                    description = form.description.data)
        
        # add to database
        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {form.username.data}!', 'success')

        # redirect user to login page
        return redirect(url_for('login'))

    return render_template('register.html', title = 'Register', form = form)

@app.route("/login", methods = ['GET', 'POST'])
def login():
    # user already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # remember login state
            login_user(user, remember = form.remember.data) 

            # store next page to redirect user
            next_page = request.args.get('next')

            flash(f'You have been logged in', 'success')

            # redirect user to current page or homepage
            if next_page or 'url' in session:
                return redirect(session['url'])
                # return redirect(next_page)
            else:
                return redirect(url_for('home'))  
        else:
            flash(f'Login Failed. Please check your email and password', 'danger')
    return render_template('login.html', title = 'Login', form = form)

@app.route("/logout")
def logout():
    logout_user()
    if "url" in session:
        return redirect(session['url'])
    else:
        return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8) # file name generate
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn) 
    form_picture.save(picture_path)

    return picture_fn

@app.route('/account', methods = ['GET', 'POST'])
@login_required #require login to access this page
def account(): 
    # store previous page into session for auto redirect
    session['url'] = url_for('account')

    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.description = form.description.data

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.description.data = current_user.description
    
    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)

    return render_template('account.html', title = 'Account', image_file = image_file, form = form)


@app.route("/article/new", methods = ['GET', 'POST'])
@login_required
def new_article():
    # Only reporter can access this page
    if current_user.type_user:
        form = ArticleForm()
        if form.validate_on_submit():
            post = Post(title = form.title.data, 
                    description = form.description.data, 
                    content = form.content.data, 
                    author = current_user,
                    category = form.category.data)
            
            # add post to database
            db.session.add(post)
            db.session.commit()

            flash('Your post has been created', 'success')
            return redirect(url_for('home'))
        return render_template('create_article.html', title = 'New Article', form = form, legend = 'New article')
    else:
        print("You cant access to this page")

# dynamic url
@app.route("/article/<int:post_id>")
def article(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('article.html', title = post.title, post = post)


@app.route("/article/<int:post_id>/update", methods = ['GET', 'POST'])
@login_required
def update_article(post_id):
    if current_user.type_user:
        post = Post.query.get_or_404(post_id)
        if post.author != current_user:
            abort(403)
        form = ArticleForm()

        if form.validate_on_submit():
            post.title = form.title.data 
            post.content = form.content.data 
            post.description = form.description.data
            post.category = form.category.data

            db.session.commit()
            flash('Your post has been updated', 'success')
            return redirect(url_for('article', post_id = post.id))
        elif request.method == 'GET':
            # assign data to input field
            form.title.data = post.title
            form.content.data = post.content
            form.description.data = post.description
            form.category.data = post.category

        return render_template('create_article.html', title = 'Update Article', form = form, legend = 'Update article')


@app.route("/article/<int:post_id>/delete", methods = ['POST'])
@login_required
def delete_article(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    # delete
    db.session.delete(post)
    db.session.commit()
    flash('Your post: \'' + post.title + '\' has been deleted', 'success')
    return redirect(url_for('home'))