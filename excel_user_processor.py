import os
import pandas as pd
from werkzeug.security import generate_password_hash
from flask import current_app

def extract_users_from_excel(excel_file):
    """
    Extract user information from an Excel file in Masar format
    
    Args:
        excel_file: The uploaded Excel file object
    
    Returns:
        A list of dictionaries containing user information
    """
    users = []
    
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file)
        
        # Check if the dataframe is empty
        if df.empty:
            return {'error': 'The Excel file is empty'}
        
        # Get the column names
        columns = df.columns.tolist()
        
        # Check if we have at least 5 columns (account name, student name, and secret code in fifth column)
        if len(columns) < 5:
            return {'error': 'The Excel file does not have enough columns'}
        
        # Process each row in the Excel file
        for index, row in df.iterrows():
            # Skip rows with empty values in essential columns
            if pd.isna(row[0]) or pd.isna(row[1]) or pd.isna(row[4]):
                continue
                
            # Extract user information
            # First column: account name (username)
            # Second column: student name (full name)
            # Fifth column: secret code (password)
            user = {
                'username': str(row[0]).strip(),
                'full_name': str(row[1]).strip(),
                'secret_code': str(row[4]).strip()
            }
            
            users.append(user)
        
        if not users:
            return {'error': 'No valid user data found in the Excel file'}
            
        return users
    
    except Exception as e:
        current_app.logger.error(f"Error processing Excel file: {str(e)}")
        return {'error': f'Error processing Excel file: {str(e)}'}

def create_users_from_data(user_data, default_role, section_id, default_password):
    """
    Create user accounts from the extracted data
    
    Args:
        user_data: List of dictionaries containing user information
        default_role: Role to assign to all users
        section_id: Section ID for student accounts
        default_password: Default password for all accounts (used as fallback if secret_code is not available)
    
    Returns:
        A dictionary with success/error information
    """
    from app import db, User
    
    created_users = []
    errors = []
    
    for user in user_data:
        try:
            # Generate email from username
            email = f"{user['username']}@school.com"
            
            # Check if user already exists
            existing_user = User.query.filter(
                (User.username == user['username']) | (User.email == email)
            ).first()
            
            if existing_user:
                errors.append(f"User {user['username']} already exists")
                continue
            
            # Use the secret_code as the password
            # If secret_code is not available, fall back to default_password
            user_password = user.get('secret_code', default_password)
            
            # Create new user
            new_user = User(
                username=user['username'],
                email=email,
                password_hash=generate_password_hash(user_password),
                role=default_role,
                section_id=int(section_id) if default_role == 'student' and section_id else None
            )
            
            db.session.add(new_user)
            created_users.append(user)
        
        except Exception as e:
            current_app.logger.error(f"Error creating user {user['username']}: {str(e)}")
            errors.append(f"Error creating user {user['username']}: {str(e)}")
    
    # Commit all successful user creations
    if created_users:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            return {'error': f'Database error: {str(e)}', 'created': [], 'errors': errors}
    
    return {
        'created': created_users,
        'errors': errors
    }
