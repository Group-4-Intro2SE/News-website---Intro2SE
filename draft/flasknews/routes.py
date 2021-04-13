from flask import render_template, url_for, flash, redirect
from flasknews import app
from flasknews.forms import RegistrationForm, LoginForm
from flasknews.models import User, Post

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
    return render_template('home.html', posts = posts)

@app.route("/about")
def about():
    return render_template('about.html', title = 'About')

@app.route("/register", methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))

    return render_template('register.html', title = 'Register', form = form)

@app.route("/login", methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash(f'You have been logged in', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Login Failed. Please check your email and password', 'danger')
    return render_template('login.html', title = 'Login', form = form)
