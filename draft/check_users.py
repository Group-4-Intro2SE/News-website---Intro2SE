from flasknews import db
from flasknews.models import User, Post 

print(User.query.all())
print(Post.query.all())



# db.create_all()