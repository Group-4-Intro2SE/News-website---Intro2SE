from flask import render_template, url_for, flash, redirect, request
from flasknews import app, db, bcrypt
from flasknews.forms import RegistrationForm, LoginForm
from flasknews.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

session = {}
posts = [
    {
        'author': 'Trmúa Hmề',
        'title': 'Article 1',
        'content': 'Cách để trở thành Trmúa Hmề trong mắt người khác official',
        'date_posted': 'April 20, 2021'
    },
    {
        'author': 'Trmúa Hmề bủh',
        'title': 'Article 2',
        'content': 'Cách để trở thành Trmúa Hmề dảk',
        'date_posted': 'April 20, 2021'
    },
]

@app.route("/")
@app.route("/home")
def home():
    # store previous page into session for auto redirect   
    session['url'] = url_for('home')

    return render_template('home.html', posts = posts)

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

@app.route("/warticle")
def warticle():
    return

@app.route('/account')
@login_required #require login to access this page
def account(): 
    # store previous page into session for auto redirect
    session['url'] = url_for('account')

    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)

    return render_template('account.html', title = 'Account', image_file = image_file)
