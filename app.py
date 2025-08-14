import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import cloudinary
import cloudinary.uploader
from datetime import datetime
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==================================================
<<<<<<< HEAD
# Load env variables
# ==================================================
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')

# ==================================================
# Database Configuration
# ==================================================
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
if db_url and "sslmode" not in db_url:
    db_url += "?sslmode=require"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///art_gallery.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ==================================================
# Cloudinary Config
# ==================================================
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

=======
# Load environment variables
# ==================================================
load_dotenv()

>>>>>>> cf5a550d0a932cfc51955a1aeca06b527f20fa7a
# ==================================================
# Email Sending Utility
# ==================================================
def send_email(to_email, subject, body):
    gmail_user = os.getenv('EMAIL_USER')
    gmail_password = os.getenv('EMAIL_PASSWORD')
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.close()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# ==================================================
<<<<<<< HEAD
=======
# Flask App Setup
# ==================================================
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')

# ==================================================
# Database Configuration
# ==================================================
db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///art_gallery.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ==================================================
# Cloudinary Configuration
# ==================================================
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# ==================================================
>>>>>>> cf5a550d0a932cfc51955a1aeca06b527f20fa7a
# Models
# ==================================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    avatar_url = db.Column(db.String(255), default='')
    bio = db.Column(db.Text, default='')

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('art_post.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    post = db.relationship('ArtPost', backref=db.backref(
        'comments', lazy=True, cascade="all, delete-orphan"))

class ArtPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

    def like_count(self):
        return self.likes.count()

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('art_post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)

User.likes = db.relationship('Like', backref='user', lazy='dynamic')
ArtPost.likes = db.relationship('Like', backref='post', lazy='dynamic')

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('messages', lazy=True))

# ==================================================
# Context Processor
# ==================================================
@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    current_user = User.query.get(user_id) if user_id else None
    return dict(
        current_user=current_user,
        CLOUDINARY_CLOUD_NAME=os.getenv('CLOUDINARY_CLOUD_NAME'),
        CLOUDINARY_AVATAR_PRESET="avatar_unsigned_preset"
    )

# ==================================================
# Routes
# ==================================================
@app.route('/')
def gallery():
    posts = ArtPost.query.order_by(ArtPost.created_at.desc()).all()
    return render_template('gallery.html', posts=posts)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    results = []
    if query:
        results = ArtPost.query.filter(
            ArtPost.title.ilike(f"%{query}%")
        ).order_by(ArtPost.created_at.desc()).all()
    return render_template('search_results.html', posts=results, query=query)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        u, e, p = request.form['username'], request.form['email'], request.form['password']
        if User.query.filter_by(username=u).first() or User.query.filter_by(email=e).first():
            return jsonify({'error': 'User exists'}), 400
        user = User(username=u, email=e)
        user.set_password(p)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('gallery'))
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            session['user_id'] = user.id
            return redirect(url_for('gallery'))
        return jsonify({'error': 'Invalid'}), 401
    return render_template('signin.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    if request.method == 'POST':
        file = request.files['image']
        res = cloudinary.uploader.upload(file)
        post = ArtPost(
            title=request.form['title'],
            caption=request.form['caption'],
            image_url=res['secure_url'],
            user_id=session['user_id']
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('gallery'))
    return render_template('upload.html')

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    msgs = ChatMessage.query.order_by(ChatMessage.created_at.desc()).limit(50).all()
    return render_template('chat.html', messages=msgs)

@app.route('/api/chat/send', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Auth required'}), 401
    msg = ChatMessage(message=request.json['message'], user_id=session['user_id'])
    db.session.add(msg)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    user = User.query.get(user_id)
    post = ArtPost.query.get_or_404(post_id)
    if not (user.is_admin or post.user_id == user.id):
        return jsonify({'error': 'Permission denied'}), 403
    db.session.delete(post)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('gallery'))

@app.route('/art/<int:post_id>')
def art_detail(post_id):
    post = ArtPost.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()
    return render_template('art_detail.html', post=post, comments=comments)

@app.route('/user/<int:user_id>')
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = ArtPost.query.filter_by(user_id=user.id).order_by(ArtPost.created_at.desc()).all()
    is_owner = session.get('user_id') == user.id
    return render_template('profile.html', profile_user=user, posts=posts, is_owner=is_owner)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('signin'))
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()

        if username and username != user.username and User.query.filter_by(username=username).first():
            return render_template('settings.html', user=user, error='Username already taken')
        if email and email != user.email and User.query.filter_by(email=email).first():
            return render_template('settings.html', user=user, error='Email already in use')

        if username:
            user.username = username
        if email:
            user.email = email

        avatar_url = request.form.get('avatar_url', '').strip()
        if avatar_url:
            user.avatar_url = avatar_url

        bio = request.form.get('bio', '').strip()
        if bio is not None:
            user.bio = bio

        new_pw = request.form.get('new_password', '').strip()
        if new_pw:
            user.set_password(new_pw)

        db.session.commit()
        return redirect(url_for('user_profile', user_id=user.id))

    return render_template('settings.html', user=user)

@app.route('/art/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    text = request.form.get('text', '').strip()
    if not text:
        return redirect(url_for('art_detail', post_id=post_id))
    c = Comment(text=text, user_id=session['user_id'], post_id=post_id)
    db.session.add(c)
    db.session.commit()

    post = ArtPost.query.get_or_404(post_id)
    owner = User.query.get(post.user_id)
    if owner and owner.email:
        subject = "YOUR POST GOT A COMMENT"
        body = f"Your artwork '{post.title}' received a new comment:\n\n\"{text}\"\n\nVisit your post to reply."
        send_email(owner.email, subject, body)

    return redirect(url_for('art_detail', post_id=post_id))

@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    user_id = session['user_id']
    post = ArtPost.query.get_or_404(post_id)
    existing = Like.query.filter_by(user_id=user_id, post_id=post.id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'status': 'unliked', 'likes': post.like_count()})
    else:
        like = Like(user_id=user_id, post_id=post.id)
        db.session.add(like)
        db.session.commit()
        return jsonify({'status': 'liked', 'likes': post.like_count()})

@app.route('/users')
def users_list():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('signin'))
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        abort(403)
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users.html', users=users)

@app.route('/admin')
def admin_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('signin'))
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        abort(403)
    user_count = User.query.count()
    artwork_count = ArtPost.query.count()
    comment_count = Comment.query.count()
    return render_template('admin_dashboard.html',
                           user_count=user_count,
                           artwork_count=artwork_count,
                           comment_count=comment_count)
<<<<<<< HEAD
=======

# ==================================================
# Main Entry
# ==================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        if admin_email and not User.query.filter_by(email=admin_email).first():
            admin = User(username=admin_username, email=admin_email, is_admin=True)
            admin.set_password(admin_password or "changeme")
            db.session.add(admin)
            db.session.commit()
    app.run(debug=False)
>>>>>>> cf5a550d0a932cfc51955a1aeca06b527f20fa7a
