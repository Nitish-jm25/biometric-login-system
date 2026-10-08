import sqlite3
from config import DATABASE_PATH


def get_connection():
    """Create a SQLite database connection."""

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """Create all required database tables."""

    connection = get_connection()

    cursor = connection.cursor()

    # Users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Face samples
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS face_samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            face_image BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
            REFERENCES users(user_id)
        )
    """)

    # Login history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            status TEXT NOT NULL,
            confidence REAL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()

    connection.close()


def get_user(user_id):
    """Get a user by User ID."""

    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    connection.close()

    return user


def create_user(user_id, name):
    """Create a new user."""

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO users
        (user_id, name)
        VALUES (?, ?)
        """,
        (user_id, name)
    )

    connection.commit()

    connection.close()


def add_face_sample(user_id, face_image):
    """Store a face image."""

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO face_samples
        (user_id, face_image)
        VALUES (?, ?)
        """,
        (user_id, face_image)
    )

    connection.commit()

    connection.close()


def get_face_samples(user_id):
    """Get all face samples for a user."""

    connection = get_connection()

    samples = connection.execute(
        """
        SELECT *
        FROM face_samples
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return samples


def get_all_face_samples():
    """Get all registered face samples."""

    connection = get_connection()

    samples = connection.execute(
        """
        SELECT
            user_id,
            face_image
        FROM face_samples
        """
    ).fetchall()

    connection.close()

    return samples


def get_all_users():
    """Get all registered users."""

    connection = get_connection()

    users = connection.execute(
        """
        SELECT
            id,
            user_id,
            name,
            created_at
        FROM users
        ORDER BY created_at DESC
        """
    ).fetchall()

    connection.close()

    return users


def record_login(user_id, status, confidence=None):
    """Record a login attempt."""

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO login_history
        (user_id, status, confidence)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            status,
            confidence
        )
    )

    connection.commit()

    connection.close()


def get_login_history(limit=50):
    """Get recent login attempts."""

    connection = get_connection()

    history = connection.execute(
        """
        SELECT
            id,
            user_id,
            status,
            confidence,
            login_time
        FROM login_history
        ORDER BY login_time DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    connection.close()

    return history


def get_statistics():
    """Get dashboard statistics."""

    connection = get_connection()

    total_users = connection.execute(
        "SELECT COUNT(*) AS count FROM users"
    ).fetchone()["count"]

    total_attempts = connection.execute(
        "SELECT COUNT(*) AS count FROM login_history"
    ).fetchone()["count"]

    successful_logins = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM login_history
        WHERE status = 'SUCCESS'
        """
    ).fetchone()["count"]

    failed_logins = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM login_history
        WHERE status = 'FAILED'
        """
    ).fetchone()["count"]

    connection.close()

    return {
        "total_users": total_users,
        "total_attempts": total_attempts,
        "successful_logins": successful_logins,
        "failed_logins": failed_logins
    }