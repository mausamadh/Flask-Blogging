__author__ = 'mausam'

from flask import Flask, render_template, request, session, make_response
from passlib.hash import sha256_crypt

from src.common.database import Database
from src.models.blog import Blog
from src.models.post import Post
from src.models.user import User

app = Flask(__name__)  # '__main__'
app.secret_key = "mausam"

email = None


@app.route('/')
def home_template():
    return render_template('main.html')


@app.route('/login')  # www.my_site.com/api/login
def login_template():
    return render_template('login.html')
    # return "hello, world"


@app.route('/register')  # 127.0.0.1:4995/register
def register_template():
    return render_template('register.html')


@app.route('/signout')
def signout():
    try:
        session.pop('email', None)
    finally:
        return render_template('main.html')


@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/auth/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    if User.login_valid(email, password):
        User.login(email)
    else:
        session['email'] = True
        return render_template('main.html')

    return render_template('profile.html', user=session['email'])


@app.route('/auth/register', methods=['POST'])
def register_user():
    email = request.form['email']
    password = sha256_crypt.encrypt(request.form['password'])

    User.register(email, password)
    user = User.get_by_email(session['email'])
    print(user)

    return render_template('profile.html', user=user)


@app.route('/profile', methods=['GET'])
def profile():
    try:
        email = session['email']
        user = User.get_by_email(email)
        return render_template('profile.html', user=user)
    except KeyError:
        return render_template('main.html')


@app.route('/auth/updateProfile', methods=["POST"])
def updateProfile():
    email = session['email']
    name = request.form['name']
    phone = request.form['phone']
    qualification = request.form['qualification']
    location = request.form['location']
    teachingexperience = request.form['teachingexperience']
    preferredtime = request.form['preferredtime']
    user = User.get_by_email(email)
    user.updateprofile(email, name, phone, qualification, location, teachingexperience, preferredtime)
    print("user updated successfully")

    return render_template('main.html')


@app.route('/updateProfile')
def updateprofile_template():
    return render_template('updateprofile.html')


@app.route('/blogs/<string:user_id>')
@app.route('/blogs')
def user_blogs(user_id=None):
    """

    :param user_id:
    :return:
    """
    if user_id is not None:
        user = User.get_by_id(user_id)
    else:
        user = User.get_by_email(session['email'])

    blogs = user.get_blogs()

    return render_template("user_blogs.html", blogs=blogs, email=user.email)


@app.route('/allblogs')
def all_blogs():
    """

    :param user_id:
    :return:
    """

    blogs = Database.find_all(collection='blogs')

    return render_template("blogs.html", blogs=blogs)


@app.route('/allusers')
def all_users():
    """

    :param user_id:
    :return:
    """

    users = Database.find_all(collection='users')

    return render_template("allusers.html", users=users)


@app.route('/posts/<string:blog_id>')
def blog_posts(blog_id):
    """

    :param blog_id:
    :return:
    """
    blog = Blog.from_mongo(blog_id)
    posts = blog.get_posts()

    return render_template('posts.html', posts=posts, blog_title=blog.title, blog_id=blog._id,
                           blog_description=blog.description)


@app.route('/blogs/new', methods=['POST', 'GET'])
def create_new_blog():
    """

    :return:
    """
    if request.method == 'GET':
        return render_template('new_blog.html')
    else:
        title = request.form['title']
        description = request.form['description']
        user = User.get_by_email(session['email'])

        new_blog = Blog(user.email, title, description, user._id)
        new_blog.save_to_mongo()

        return make_response(user_blogs(user._id))


@app.route('/posts/new/<string:blog_id>', methods=['POST', 'GET'])
def create_new_post(blog_id):
    """

    :param blog_id:
    :return:
    """
    if request.method == 'GET':
        return render_template('new_post.html', blog_id=blog_id)
    else:
        title = request.form['title']
        content = request.form['content']
        user = User.get_by_email(session['email'])

        new_post = Post(blog_id, title, content, user.email)
        new_post.save_to_mongo()

        return make_response(blog_posts(blog_id))


if __name__ == '__main__':
    app.run(debug=True)
