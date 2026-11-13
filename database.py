
import sqlite3
from pathlib import Path


class ClipboardDatabase:

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.image_dir = self.data_dir / "images"

        self.image_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.data_dir / "clipboard.db"

        self.connection = sqlite3.connect(self.db_path)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                content TEXT,
                image_path TEXT,
                fingerprint TEXT UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.connection.commit()

    def add_text(self, text, fingerprint):
        self.connection.execute("""
            INSERT OR IGNORE INTO history
            (type, content, fingerprint)
            VALUES (?, ?, ?)
        """, ("text", text, fingerprint))

        self.connection.commit()

    def add_image(self, image, fingerprint):
        filename = f"{fingerprint}.png"
        image_path = self.image_dir / filename

        if not image_path.exists():
            image.save(str(image_path), "PNG")

        self.connection.execute("""
            INSERT OR IGNORE INTO history
            (type, image_path, fingerprint)
            VALUES (?, ?, ?)
        """, ("image", str(image_path), fingerprint))

        self.connection.commit()

    def get_history(self):
        cursor = self.connection.execute("""
            SELECT type, content, image_path, created_at, fingerprint
            FROM history
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    def close(self):
        self.connection.close()
