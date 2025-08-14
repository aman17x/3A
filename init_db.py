from app import db, app, User
import os

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='versionx17@gmail.com').first():
        admin = User(
            username='verse17',
            email='versionx17@gmail.com',
            is_admin=True
        )
        admin.set_password(os.getenv("ADMIN_PASSWORD", "your-strong-password"))
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created.")
    else:
        print("ℹ Admin user already exists.")
