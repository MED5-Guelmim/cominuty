import sqlite3
import os

def migrate_database():
    """Add new columns to existing database"""
    db_path = 'instance/school_platform.db'
    
    if not os.path.exists(db_path):
        print("Database doesn't exist yet. No migration needed.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add section column to user table
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN section VARCHAR(50)")
            print("Added section column to user table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Section column already exists in user table")
            else:
                raise
        
        # Add section column to lesson table
        try:
            cursor.execute("ALTER TABLE lesson ADD COLUMN section VARCHAR(50)")
            print("Added section column to lesson table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Section column already exists in lesson table")
            else:
                raise
        
        # Add file_path column to lesson table
        try:
            cursor.execute("ALTER TABLE lesson ADD COLUMN file_path VARCHAR(500)")
            print("Added file_path column to lesson table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("File_path column already exists in lesson table")
            else:
                raise
        
        # Add file_type column to lesson table
        try:
            cursor.execute("ALTER TABLE lesson ADD COLUMN file_type VARCHAR(50)")
            print("Added file_type column to lesson table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("File_type column already exists in lesson table")
            else:
                raise
        
        # Add section column to quiz table
        try:
            cursor.execute("ALTER TABLE quiz ADD COLUMN section VARCHAR(50)")
            print("Added section column to quiz table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Section column already exists in quiz table")
            else:
                raise
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()