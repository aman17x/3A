# patch_db.py
from app import db
from sqlalchemy import text

with db.engine.connect() as conn:
    # Add avatar_url column if missing
    conn.execute(text("ALTER TABLE user ADD COLUMN avatar_url VARCHAR(255) DEFAULT ''"))
    # Add bio column if missing
    conn.execute(text("ALTER TABLE user ADD COLUMN bio TEXT DEFAULT ''"))
    conn.commit()

print("✅ Columns 'avatar_url' and 'bio' added to the user table.")
