from flasknews import db
from flasknews.models import User, Post 

db.drop_all()
db.create_all()

# cach lay image tu local folder
# src="{{ url_for('static', filename='profile_pics/' + post.author.image_file) }}">


