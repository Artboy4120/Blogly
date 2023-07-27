from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secretsig'

toolbar = DebugToolbarExtension(app)

# Connect the database and create the tables
connect_db(app)

@app.route('/')
def root():
    """Show homepage with a list of posts."""
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    user = User.query.first()  # Replace this with your logic to fetch the user from the database
    return render_template("posts/homepage.html", posts=posts, user=user)

@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""
    return render_template('404.html'), 404

# User routes

@app.route('/users')
def users_index():
    """Show a page with info on all users"""
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('users/index.html', users=users)

@app.route('/users/new', methods=["GET", "POST"])
def users_new_form():
    """Show a form to create a new user or handle form submission for creating a new user"""
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        image_url = request.form['image_url'] or None

        new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/users")
    else:
        return render_template('users/new.html')

@app.route('/users/<int:user_id>', methods=["GET", "POST"])
def users_detail(user_id):
    """Show a page with info on a specific user and their posts or handle form submission for adding a new post"""
    user = User.query.get_or_404(user_id)
    first_post = user.posts[0] if user.posts else None
    other_posts = user.posts[1:]

    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']

        new_post = Post(title=title, content=content, user_id=user.id)
        db.session.add(new_post)
        db.session.commit()

        return redirect(f"/users/{user.id}")
    else:
        return render_template('users/show.html', user=user, first_post=first_post, other_posts=other_posts)

@app.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
def users_edit(user_id):
    """Show a form to edit an existing user or handle form submission for updating an existing user"""
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.image_url = request.form['image_url']
        db.session.commit()

        return redirect("/users")

    return render_template('users/edit.html', user=user)

@app.route('/users/<int:user_id>/delete', methods=["POST"])
def users_destroy(user_id):
    """Handle form submission for deleting an existing user"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")

@app.route('/users/<int:user_id>/add_post', methods=["GET", "POST"])
def add_post(user_id):
    """Add a new post for the user."""
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']

        new_post = Post(title=title, content=content, user_id=user.id)
        db.session.add(new_post)
        db.session.commit()

        return redirect(f"/posts/{new_post.id}")

    return render_template('posts/add.html', user=user)

@app.route('/posts/<int:post_id>', methods=["GET"])
def post_detail(post_id):
    """Show details of a post."""
    post = Post.query.get_or_404(post_id)
    return render_template('posts/detail.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    # Clear existing tags for the post
    post.tags.clear()

    # Get a list of selected tag IDs
    tag_ids = request.form.getlist('tags')

    # Add the selected tags to the post
    for tag_id in tag_ids:
        tag = Tag.query.get(tag_id)
        if tag:
            post.tags.append(tag)

    db.session.commit()
    return redirect(f"/users/{post.user_id}")

@app.route('/tags')
def list_tags():
    tags = Tag.query.all()
    return render_template('tags/list.html', tags=tags)

@app.route('/tags/<int:tag_id>')
def show_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/show.html', tag=tag)

@app.route('/tags/new', methods=["GET", "POST"])
def new_tag_form():
    if request.method == "POST":
        name = request.form['name']
        new_tag = Tag(name=name)
        db.session.add(new_tag)
        db.session.commit()
        return redirect('/tags')
    else:
        return render_template('tags/new.html')

@app.route('/tags/<int:tag_id>/edit', methods=["GET", "POST"])
def edit_tag_form(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    if request.method == "POST":
        tag.name = request.form['name']
        db.session.commit()
        return redirect('/tags')

    return render_template('tags/edit.html', tag=tag)

@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return redirect('/tags')

@app.route('/posts/<int:post_id>/edit', methods=["GET"])
def edit_post_form(post_id):
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('posts/edit.html', post=post, tags=tags)

# Add a new route for adding a new tag
@app.route('/tags/new', methods=["GET", "POST"])
def add_tag():
    """Add a new tag."""
    if request.method == "POST":
        name = request.form['name']
        new_tag = Tag(name=name)
        db.session.add(new_tag)
        db.session.commit()

        return redirect('/tags')

    return render_template('tags/new.html')

@app.route("/posts/new/<int:user_id>", methods=["GET", "POST"])
def new_post(user_id):
    # Retrieve the user with the given user_id from the database
    user = User.query.get(user_id)

    # Retrieve all the tags from the database
    tags = Tag.query.all()

    if request.method == "POST":
        # Get the form data for the new post
        title = request.form["title"]
        content = request.form["content"]
        selected_tags = request.form.getlist("tags")  # Get the selected tags as a list

        # Create the new post
        post = Post(title=title, content=content, user_id=user_id)

        # Add the selected tags to the post
        for tag_id in selected_tags:
            tag = Tag.query.get(tag_id)
            if tag:
                post.tags.append(tag)

        # Save the new post to the database
        db.session.add(post)
        db.session.commit()

        return redirect(url_for("user_detail", user_id=user_id))

    return render_template("posts/new_post.html", user=user, tags=tags)
    tags = Tag.query.all()
    return render_template('posts/new.html', tags=tags, user=user)




@app.route('/posts/filter/<int:tag_id>')
def filter_posts_by_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    return render_template('posts/homepage.html', posts=tag.posts)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
