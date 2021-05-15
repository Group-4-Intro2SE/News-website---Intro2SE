import os 
import secrets
from sqlalchemy import desc
from flask import render_template, url_for, flash, redirect, request, abort
from flasknews import app, db, bcrypt
from flasknews.forms import RegistrationForm, LoginForm, UpdateAccountForm, RegistrationFormReporter, ArticleForm, UpdateArticleForm, SearchForm, LoginFormAdmin
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



@app.route("/")
@app.route("/home", methods = ['GET', 'POST'])
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
    article_by_categories = []

    categories = ["Stars", 'TV Shows', "Music", "Sport", "Fashion", "Travel", "Life"]
    for cat in categories:
        query_articles = Post.query.filter_by(category = cat).order_by(desc(Post.date_posted)).all()
        article_by_categories.append(query_articles)
    # print(article_by_categories)

    image_file = url_for('static', filename = 'article_pics/')

    return render_template('home.html', posts = posts, latest = latest, article_by_categories = article_by_categories, categories = categories, len = len(categories), image_file = image_file)

@app.route("/about")
def about():
    # store previous page into session for auto redirect
    session['url'] = url_for('about')

    return render_template('about.html', title = 'About')

@app.route("/home/<cat>")
def category(cat):
    posts = Post.query.filter_by(category = cat)
    image_file = url_for('static', filename = 'article_pics/')

    return render_template('search_results.html', posts = posts, image_file = image_file)

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

def save_picture(form_picture):
    random_hex = secrets.token_hex(8) # file name generate
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn) 
    form_picture.save(picture_path)

    return picture_fn


def save_picture_2(form_picture):
    random_hex = secrets.token_hex(8) # file name generate
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/article_pics', picture_fn) 
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
            # print(form.picture.data)
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

temptemp = ''
@app.route("/article/new", methods = ['GET', 'POST'])
@login_required
def new_article():
    session['url'] = url_for('new_article')
    # Only reporter can access this page
    form = ArticleForm()

    post = Post(title = form.title.data, 
        description = form.description.data, 
        content = form.content.data, 
        author = current_user,
        category = form.category.data)
    picture_file = ''
    image_file = ''
    
    if form.validate_on_submit():
        if form.cover_image.data:
            picture_file = save_picture_2(form.cover_image.data)
            post.cover_image = picture_file
            global temptemp
            temptemp = post.cover_image

            image_file = url_for('static', filename = 'article_pics/' + temptemp)

        # add post to database
        db.session.add(post)
        db.session.commit()

        flash('Your post has been created', 'success')
        return redirect(url_for('home'))

    

    return render_template('create_article.html', title = 'New Article', form = form, legend = 'New article')

# dynamic url
@app.route("/article/<int:post_id>")
def article(post_id):
    session['url'] = url_for('article', post_id = post_id)

    post = Post.query.get_or_404(post_id)
    return render_template('article.html', title = post.title, post = post)


@app.route("/article/<int:post_id>/update", methods = ['GET', 'POST'])
@login_required
def update_article(post_id):
    if current_user.type_user:
        post = Post.query.get_or_404(post_id)
        if post.author != current_user:
            abort(403)
        form = UpdateArticleForm()

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


@app.route("/admin/dash/article/<int:post_id>/delete", methods = ['POST', 'GET'])
def delete_article(post_id):
    post = Post.query.get(post_id)
    
    # delete
    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('admin_dash_article'))

@app.route("/search", methods = ['GET', 'POST'])
def search():
    session['url'] = url_for('search')

    form = SearchForm()
    if form.validate_on_submit():
        query = form.search.data
        return redirect((url_for('search_results', query=query)))  # or what you want
        # return redirect((url_for('search_results'))) 

    return render_template('search.html', form=form, title = 'Search', legend = 'Search')

# @app.route("/results", methods = ['GET', 'POST'])
# def search_results():
#     print("ping")
#     return render_template('search_results.html')

@app.route("/search/results/<query>")
def search_results(query):
    session['url'] = url_for('search_results', query = query)

    results = []
    posts = Post.query.all()
    print(posts)
    for post in posts:
        query_lower = query.lower()
        if query_lower in post.title.lower() or query_lower in post.description.lower() or query_lower in post.content.lower():
            results.append(post)

    image_file = url_for('static', filename = 'article_pics/')
    if len(results) == 0:
        return redirect(url_for('search_error'))
    return render_template('search_results.html', query=query, posts=results, image_file = image_file)

@app.route("/search/error")
def search_error():
    session['url'] = url_for('search_error')

    image_file = url_for('static', filename = 'search_error.jpg')
    return render_template('search_error.html', image_file = image_file)


admin_state = 0

@app.route("/admin", methods = ['GET', 'POST'])
@app.route("/admin/login", methods = ['GET', 'POST'])
def admin_login():
    logout_user()
    keypass = "admin"
    global admin_state

    form = LoginFormAdmin()
    if form.validate_on_submit():
        if form.password.data == keypass:
            admin_state = 1
            return redirect(url_for('admin_dash'))
        else:
            admin_state = 0
            flash('Wrong password, please try again', 'danger')


    return render_template('admin_login.html', form = form)


@app.route("/admin/dash", methods = ['GET'])
def admin_dash():
    if not admin_state:
        return redirect(url_for('admin_login'))
    
    posts = Post.query.all()
    viewers = User.query.filter_by(type_user = 0).all()
    reporters = User.query.filter_by(type_user = 1).all()

    link = url_for('admin_dash_article')

    return render_template('admin_dash.html', posts = posts, viewers = viewers, reporters = reporters, link = link)

@app.route("/admin/dash/article")
def admin_dash_article():
    if not admin_state:
        return redirect(url_for('admin_login'))

    import pandas as pd
    import seaborn as sns 
    import matplotlib.pyplot as plt

    data = Post.query.all()
    df = pd.DataFrame([(d.id, d.date_posted) for d in data], 
                    columns=['id', 'date_posted'])

    # df['date_posted'] = df['date_posted'].dt.round('H')
    # df_group = df.groupby('date_posted')['id'].count()
    # df_group = df_group.reset_index()
    # df_group['count'] = df_group['id'].cumsum()

    # plt.style.use('ggplot')
    # sns.lineplot(x = 'date_posted', y = 'count', data = df_group)
    # plt.xlabel('Date and time posted')
    # plt.xticks(rotation=90)
    # plt.tight_layout()
    # plt.subplots_adjust(bottom=0.19)
    # plt.tick_params(axis='x', colors='black')
    # plt.tick_params(axis='y', colors='black')

    # plt.savefig('flasknews/static/article_line_plot.png')

    # image_file = url_for('static', filename = 'article_line_plot.png')
    

    return render_template('admin_dash_article.html', posts = data)

@app.route("/admin/dash/reporter")
def admin_dash_reporter():
    if not admin_state:
        return redirect(url_for('admin_login'))
    
    reporters = User.query.filter_by(type_user = 1).all()
    print(reporters)
    posts = Post.query.all()

    return render_template('admin_dash_reporter.html', reporters = reporters, posts = posts)



@app.route("/admin/dash/reporter/reg_reporter", methods = ['GET', 'POST'])
def register_reporter():
    if not admin_state:
        return redirect(url_for('admin_login'))

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
        return redirect(url_for('admin_dash'))

    return render_template('register.html', title = 'Register', form = form)


@app.route('/admin/dash/reporter/<idd>', methods = ['GET', 'POST'])
def admin_dash_reporter_account(idd): 
    if not admin_state:
        return redirect(url_for('admin_login'))

    current_user_link = User.query.filter_by(id = idd).first()

    

    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            # print(form.picture.data)
            picture_file = save_picture(form.picture.data)
            current_user_link.image_file = picture_file

        current_user_link.username = form.username.data
        current_user_link.email = form.email.data
        current_user_link.description = form.description.data

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user_link.username
        form.email.data = current_user_link.email
        form.description.data = current_user_link.description
    
    image_file = url_for('static', filename = 'profile_pics/' + current_user_link.image_file)

    return render_template('account.html', title = 'Account', image_file = image_file, form = form, current_user = current_user_link)