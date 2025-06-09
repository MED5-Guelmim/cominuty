import os
import io
import PyPDF2
from werkzeug.security import generate_password_hash
from flask import current_app

def extract_users_from_pdf(pdf_file):
    """
    Extract user information from a PDF file with form fields
    
    Args:
        pdf_file: The uploaded PDF file object
    
    Returns:
        A list of dictionaries containing user information
    """
    users = []
    
    try:
        # Read the PDF file
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Check if the PDF has form fields
        if '/AcroForm' not in pdf_reader.trailer['/Root']:
            return {'error': 'The PDF does not contain form fields'}
        
        # Get form fields from the PDF
        fields = pdf_reader.get_fields()
        
        if not fields:
            return {'error': 'No form fields found in the PDF'}
        
        # Group fields by their order in the PDF
        field_groups = {}
        
        for field_name, field_value in fields.items():
            # Extract the field value
            if isinstance(field_value, dict) and '/V' in field_value:
                value = field_value['/V']
                if isinstance(value, PyPDF2.generic.ByteStringObject):
                    value = value.decode('utf-8')
                elif isinstance(value, PyPDF2.generic.TextStringObject):
                    value = str(value)
                else:
                    value = str(value)
            else:
                value = ""
            
            # Try to determine the field order from the name
            # This is a heuristic and might need adjustment based on actual PDF structure
            parts = field_name.split('.')
            if len(parts) > 1:
                try:
                    group_id = int(parts[0])
                except ValueError:
                    # If we can't determine the order, use the field name as the group ID
                    group_id = field_name
                
                if group_id not in field_groups:
                    field_groups[group_id] = []
                
                field_groups[group_id].append(value)
        
        # Process each group of fields
        for group_id, values in field_groups.items():
            if len(values) >= 3:  # We need at least name, username, and secret code
                user = {
                    'full_name': values[0],
                    'username': values[1],
                    'secret_code': values[2]
                }
                users.append(user)
        
        return users
    
    except Exception as e:
        current_app.logger.error(f"Error processing PDF: {str(e)}")
        return {'error': f'Error processing PDF: {str(e)}'}

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
            
            # Use the secret_code from the third box as the password
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
