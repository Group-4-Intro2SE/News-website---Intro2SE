from datetime import datetime
from flasknews import db, login_manager
from flask_login import UserMixin

# get user by id in database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # 0: viewer, 1: reporter
    type_user = db.Column(db.Integer, default = 0) 

    # gender
    is_male = db.Column(db.Integer, default = 1)

    # personal description
    description = db.Column(db.String(240), nullable = False, default= "Hi, I'm a new user")

    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    # query print
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.is_male}', '{self.description}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100), nullable = False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(20))

    # query print
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}'), '{self.category}'"