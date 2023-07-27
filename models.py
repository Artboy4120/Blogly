from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class User(db.Model):
    """User model for Blogly."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.Text, default='https://tinyurl.com/nhex22ry')

    def __repr__(self):
        return f"<User id={self.id} first_name={self.first_name} last_name={self.last_name}>"

    @property
    def full_name(self):
        """Return full name of user."""
        return f"{self.first_name} {self.last_name}"


class Post(db.Model):
    """Post model for Blogly."""

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tags = db.relationship('Tag', secondary='posts_tags', backref='posts')

    @property
    def friendly_date(self):
        """Return nicely-formatted date."""
        return self.created_at.strftime("%a %b %-d  %Y, %-I:%M %p")

    # Define a relationship to the User model
    user = db.relationship('User', backref='posts')

class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    tag_posts = db.relationship('Post', secondary='posts_tags', backref='tags_posts')


class PostTag(db.Model):
    __tablename__ = 'posts_tags'
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)

def connect_db(app):
    """Connect the database to the Flask app."""
    db.app = app
    db.init_app(app)



