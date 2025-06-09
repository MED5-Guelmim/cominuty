#!/usr/bin/env python3
"""
Migration script to update the database schema for the new section system.
This script will:
1. Create the new Section table
2. Add default sections
3. Migrate existing user section data to the new system
4. Update lesson and quiz section references
"""

import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Lesson, Quiz, Section

def migrate_database():
    """Migrate the database to the new section system."""
    
    with app.app_context():
        print("Starting database migration...")
        
        # Create all tables (this will create the new Section table)
        db.create_all()
        print("✓ Database tables created/updated")
        
        # Create default sections if they don't exist
        default_sections = [
            {"name": "Common Trunk", "description": "Common trunk level for all students"},
            {"name": "First Baccalaureate", "description": "First year of baccalaureate"},
            {"name": "Second Baccalaureate", "description": "Second year of baccalaureate"},
            {"name": "Science Branch", "description": "Science specialization"},
            {"name": "Literature Branch", "description": "Literature specialization"},
            {"name": "Economics Branch", "description": "Economics specialization"}
        ]
        
        section_mapping = {}
        
        for section_data in default_sections:
            existing_section = Section.query.filter_by(name=section_data["name"]).first()
            if not existing_section:
                section = Section(
                    name=section_data["name"],
                    description=section_data["description"]
                )
                db.session.add(section)
                db.session.flush()  # Get the ID
                section_mapping[section_data["name"]] = section.id
                print(f"✓ Created section: {section_data['name']}")
            else:
                section_mapping[existing_section.name] = existing_section.id
                print(f"✓ Section already exists: {existing_section.name}")
        
        # Create mapping for old section strings to new section IDs
        old_to_new_mapping = {
            "common_trunk": "Common Trunk",
            "first_baccalaureate": "First Baccalaureate", 
            "second_baccalaureate": "Second Baccalaureate"
        }
        
        # Migrate users - check if they have the old section column
        users_updated = 0
        try:
            # Try to access the old section column
            users_with_sections = db.session.execute(
                "SELECT id, section FROM user WHERE section IS NOT NULL"
            ).fetchall()
            
            for user_id, old_section in users_with_sections:
                if old_section in old_to_new_mapping:
                    new_section_name = old_to_new_mapping[old_section]
                    if new_section_name in section_mapping:
                        new_section_id = section_mapping[new_section_name]
                        
                        # Update user with new section_id
                        db.session.execute(
                            "UPDATE user SET section_id = :section_id WHERE id = :user_id",
                            {"section_id": new_section_id, "user_id": user_id}
                        )
                        users_updated += 1
            
            print(f"✓ Migrated {users_updated} users to new section system")
            
        except Exception as e:
            print(f"Note: Could not migrate old user sections (this is normal for new installations): {e}")
        
        # Migrate lessons - check if they have the old section column
        lessons_updated = 0
        try:
            lessons_with_sections = db.session.execute(
                "SELECT id, section FROM lesson WHERE section IS NOT NULL"
            ).fetchall()
            
            for lesson_id, old_section in lessons_with_sections:
                if old_section in old_to_new_mapping:
                    new_section_name = old_to_new_mapping[old_section]
                    if new_section_name in section_mapping:
                        new_section_id = section_mapping[new_section_name]
                        
                        # Update lesson with new section_id
                        db.session.execute(
                            "UPDATE lesson SET section_id = :section_id WHERE id = :lesson_id",
                            {"section_id": new_section_id, "lesson_id": lesson_id}
                        )
                        lessons_updated += 1
            
            print(f"✓ Migrated {lessons_updated} lessons to new section system")
            
        except Exception as e:
            print(f"Note: Could not migrate old lesson sections (this is normal for new installations): {e}")
        
        # Migrate quizzes - check if they have the old section column
        quizzes_updated = 0
        try:
            quizzes_with_sections = db.session.execute(
                "SELECT id, section FROM quiz WHERE section IS NOT NULL"
            ).fetchall()
            
            for quiz_id, old_section in quizzes_with_sections:
                if old_section in old_to_new_mapping:
                    new_section_name = old_to_new_mapping[old_section]
                    if new_section_name in section_mapping:
                        new_section_id = section_mapping[new_section_name]
                        
                        # Update quiz with new section_id
                        db.session.execute(
                            "UPDATE quiz SET section_id = :section_id WHERE id = :quiz_id",
                            {"section_id": new_section_id, "quiz_id": quiz_id}
                        )
                        quizzes_updated += 1
            
            print(f"✓ Migrated {quizzes_updated} quizzes to new section system")
            
        except Exception as e:
            print(f"Note: Could not migrate old quiz sections (this is normal for new installations): {e}")
        
        # Commit all changes
        db.session.commit()
        print("✓ All changes committed to database")
        
        print("\nMigration completed successfully!")
        print(f"- Created/verified {len(default_sections)} sections")
        print(f"- Migrated {users_updated} users")
        print(f"- Migrated {lessons_updated} lessons") 
        print(f"- Migrated {quizzes_updated} quizzes")
        
        # Show current sections
        print("\nCurrent sections in database:")
        sections = Section.query.all()
        for section in sections:
            user_count = User.query.filter_by(section_id=section.id).count()
            print(f"  - {section.name}: {user_count} users")

if __name__ == "__main__":
    migrate_database()