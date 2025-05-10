import sqlite3

# Connect to SQLite database (it will create chat_history.db if not exists)
conn = sqlite3.connect("chat_history.db")
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT NOT NULL,
        detected_mood TEXT NOT NULL,
        confidence_score REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Save changes and close connection
conn.commit()
conn.close()

print("✅ Database and table created successfully!")
