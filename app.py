from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
import io
from ai_analytics import get_analytics_instance
from translations import get_translation, get_all_translations, translations
from pdf_user_processor import extract_users_from_pdf
from excel_user_processor import extract_users_from_excel, create_users_from_data

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'gif', 'xlsx', 'xls', 'mp4', 'webm', 'ogg'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}
ALLOWED_EXCEL_EXTENSIONS = {'xlsx', 'xls'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_pdf_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_PDF_EXTENSIONS

def allowed_excel_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXCEL_EXTENSIONS

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Add custom Jinja2 filter for JSON parsing
@app.template_filter('from_json')
def from_json_filter(value):
    if value:
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []
    return []

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database Models
class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='section_ref', lazy=True)
    lessons = db.relationship('Lesson', backref='section_ref', lazy=True)
    quizzes = db.relationship('Quiz', backref='section_ref', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, student
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))  # Reference to Section table
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='author', lazy=True)
    quizzes = db.relationship('Quiz', backref='author', lazy=True)
    quiz_attempts = db.relationship('QuizAttempt', backref='student', lazy=True)
    interactions = db.relationship('StudentInteraction', backref='student', lazy=True)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)  # Made optional for file-only lessons
    content_type = db.Column(db.String(20), default='file_upload')  # Changed default to file_upload
    file_url = db.Column(db.String(200))
    file_path = db.Column(db.String(500))  # For uploaded files
    file_type = db.Column(db.String(50))   # pdf, docx, pptx, jpg, png, etc.
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)  # Reference to Section table
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)  # Reference to Section table
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=False)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # multiple_choice, true_false, short_answer
    options = db.Column(db.Text)  # JSON string for multiple choice options
    correct_answer = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, default=1)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Float, default=0)
    total_points = db.Column(db.Integer, default=0)
    answers = db.Column(db.Text)  # JSON string of answers
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class StudentInteraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    interaction_type = db.Column(db.String(50), nullable=False)  # lesson_view, quiz_attempt, puzzle_solve
    content_id = db.Column(db.Integer)  # ID of lesson, quiz, or puzzle
    duration = db.Column(db.Integer)  # Time spent in seconds
    performance_score = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

# Registration route removed - only admin can create users now

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Language support
@app.route('/set_language/<language>')
def set_language(language):
    session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.context_processor
def inject_language():
    current_lang = session.get('language', 'en')
    return dict(
        current_language=current_lang,
        t=lambda key: get_translation(key, current_lang),
        translations=get_all_translations(current_lang)
    )

# Dashboard Routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get statistics
    total_users = User.query.count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_students = User.query.filter_by(role='student').count()
    total_lessons = Lesson.query.count()
    total_quizzes = Quiz.query.count()
    total_sections = Section.query.count()
    
    # Get all users and sections for management
    all_users = User.query.all()
    all_sections = Section.query.all()
    
    # Get recent activities
    recent_activities = []
    
    # Get recent quiz attempts
    quiz_attempts = QuizAttempt.query.order_by(QuizAttempt.completed_at.desc()).limit(5).all()
    for attempt in quiz_attempts:
        student = User.query.get(attempt.student_id)
        quiz = Quiz.query.get(attempt.quiz_id)
        if student and quiz:
            recent_activities.append({
                'time': attempt.completed_at,
                'user': student.username,
                'action': 'quiz_completed',
                'details': f"{quiz.title} - {get_translation('score', session.get('language', 'en'))}: {int((attempt.score / attempt.total_points) * 100)}%"
            })
    
    # Get recent lesson creations
    lessons = Lesson.query.order_by(Lesson.created_at.desc()).limit(5).all()
    for lesson in lessons:
        teacher = User.query.get(lesson.teacher_id)
        if teacher:
            recent_activities.append({
                'time': lesson.created_at,
                'user': teacher.username,
                'action': 'lesson_created',
                'details': lesson.title
            })
    
    # Get recent student interactions (lesson views)
    interactions = StudentInteraction.query.filter_by(interaction_type='lesson_view').order_by(StudentInteraction.timestamp.desc()).limit(5).all()
    for interaction in interactions:
        student = User.query.get(interaction.student_id)
        lesson = Lesson.query.get(interaction.content_id)
        if student and lesson:
            recent_activities.append({
                'time': interaction.timestamp,
                'user': student.username,
                'action': 'lesson_viewed',
                'details': lesson.title
            })
    
    # Sort activities by time (most recent first)
    recent_activities.sort(key=lambda x: x['time'], reverse=True)
    recent_activities = recent_activities[:10]  # Limit to 10 most recent activities
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_teachers=total_teachers,
                         total_students=total_students,
                         total_lessons=total_lessons,
                         total_quizzes=total_quizzes,
                         total_sections=total_sections,
                         all_users=all_users,
                         all_sections=all_sections,
                         recent_activities=recent_activities)

# Admin section management routes
@app.route('/admin/create_section', methods=['POST'])
@login_required
def admin_create_section():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    name = request.form['name']
    description = request.form.get('description', '')
    
    # Check if section already exists
    if Section.query.filter_by(name=name).first():
        flash('Section already exists')
        return redirect(url_for('admin_dashboard'))
    
    # Create new section
    section = Section(
        name=name,
        description=description
    )
    db.session.add(section)
    db.session.commit()
    
    flash(f'Section "{name}" created successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_section/<int:section_id>', methods=['POST'])
@login_required
def admin_delete_section(section_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    section = Section.query.get_or_404(section_id)
    
    # Check if section has users
    if section.users:
        flash(f'Cannot delete section "{section.name}" - it has {len(section.users)} users assigned')
        return redirect(url_for('admin_dashboard'))
    
    # Delete section
    db.session.delete(section)
    db.session.commit()
    
    flash(f'Section "{section.name}" deleted successfully')
    return redirect(url_for('admin_dashboard'))

# Admin user management routes
@app.route('/admin/create_user', methods=['POST'])
@login_required
def admin_create_user():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']
    
    # Check if section_id is provided for student accounts
    if role == 'student' and not request.form.get('section_id'):
        flash('Section is required for student accounts')
        return redirect(url_for('admin_dashboard'))
    
    section_id = request.form.get('section_id') if role == 'student' else None
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        flash('Username already exists')
        return redirect(url_for('admin_dashboard'))
    
    if User.query.filter_by(email=email).first():
        flash('Email already exists')
        return redirect(url_for('admin_dashboard'))
    
    # Create new user
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        section_id=int(section_id) if section_id else None
    )
    db.session.add(user)
    db.session.commit()
    
    flash(f'{role.title()} account created successfully for {username}')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('Cannot delete your own account')
        return redirect(url_for('admin_dashboard'))
    
    # Delete user and related data
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} deleted successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_all_users', methods=['POST'])
@login_required
def admin_delete_all_users():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get all users except the current admin
    users_to_delete = User.query.filter(User.id != current_user.id).all()
    
    # Delete all users
    count = 0
    for user in users_to_delete:
        db.session.delete(user)
        count += 1
    
    db.session.commit()
    
    flash(f'Successfully deleted {count} users')
    return redirect(url_for('user_management'))

@app.route('/admin/users')
@login_required
def user_management():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get statistics
    total_users = User.query.count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_students = User.query.filter_by(role='student').count()
    total_admins = User.query.filter_by(role='admin').count()
    
    # Get all users and sections for management
    all_users = User.query.all()
    all_sections = Section.query.all()
    
    return render_template('user_management.html',
                         total_users=total_users,
                         total_teachers=total_teachers,
                         total_students=total_students,
                         total_admins=total_admins,
                         all_users=all_users,
                         all_sections=all_sections)

@app.route('/admin/upload_users', methods=['GET', 'POST'])
@login_required
def upload_users():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get all sections for the dropdown
    all_sections = Section.query.all()
    
    # If it's just a GET request, render the template
    if request.method == 'GET':
        return render_template('upload_users.html', all_sections=all_sections)
    
    # No preview data by default
    preview_data = None
    preview_data_json = None
    
    return render_template('upload_users.html', 
                          all_sections=all_sections,
                          preview_data=preview_data,
                          preview_data_json=preview_data_json)

@app.route('/admin/upload_users_pdf', methods=['POST'])
@login_required
def upload_users_pdf():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get all sections for the dropdown
    all_sections = Section.query.all()
    
    # Check if a file was uploaded
    if 'pdf_file' not in request.files:
        flash('No file part')
        return redirect(url_for('upload_users'))
    
    file = request.files['pdf_file']
    
    # Check if the file is empty
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('upload_users'))
    
    # Get form data
    default_role = request.form.get('default_role', 'student')
    section_id = request.form.get('section_id', '')
    default_password = request.form.get('default_password', 'changeme')
    
    # Check if section is provided for student accounts
    if default_role == 'student' and not section_id:
        flash('Section is required for student accounts')
        return redirect(url_for('upload_users'))
    
    # Process the file based on its type
    file_content = file.read()
    file.seek(0)  # Reset file pointer to beginning
    
    # Check if the file is an Excel file
    if allowed_excel_file(file.filename):
        # Extract user data from Excel
        users_data = extract_users_from_excel(io.BytesIO(file_content))
    # Check if the file is a PDF
    elif allowed_pdf_file(file.filename):
        # Extract user data from PDF
        users_data = extract_users_from_pdf(io.BytesIO(file_content))
    else:
        flash('Only PDF and Excel files are allowed')
        return redirect(url_for('upload_users'))
    
    # Check if there was an error
    if isinstance(users_data, dict) and 'error' in users_data:
        flash(users_data['error'])
        return redirect(url_for('upload_users'))
    
    # If no users were found
    if not users_data:
        flash('No user data found in the PDF')
        return redirect(url_for('upload_users'))
    
    # Add role and section information to preview data
    preview_data = []
    for user in users_data:
        user_info = user.copy()
        user_info['role'] = default_role
        
        # Add section name if applicable
        if default_role == 'student' and section_id:
            section = Section.query.get(int(section_id))
            user_info['section_name'] = section.name if section else 'Unknown'
        else:
            user_info['section_name'] = 'N/A'
        
        preview_data.append(user_info)
    
    # Convert preview data to JSON for the hidden form field
    preview_data_json = json.dumps({
        'users': preview_data,
        'default_role': default_role,
        'section_id': section_id,
        'default_password': default_password
    })
    
    return render_template('upload_users.html',
                          all_sections=all_sections,
                          preview_data=preview_data,
                          preview_data_json=preview_data_json)

@app.route('/admin/confirm_users_upload', methods=['POST'])
@login_required
def confirm_users_upload():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get the JSON data from the form
    confirm_data = request.form.get('confirm_data', '{}')
    
    try:
        data = json.loads(confirm_data)
        users = data.get('users', [])
        default_role = data.get('default_role', 'student')
        section_id = data.get('section_id', '')
        default_password = data.get('default_password', 'changeme')
        
        # Create the users
        result = create_users_from_data(users, default_role, section_id, default_password)
        
        # Check for errors
        if 'error' in result:
            flash(result['error'])
            return redirect(url_for('upload_users'))
        
        # Show success message
        created_count = len(result['created'])
        error_count = len(result['errors'])
        
        if created_count > 0:
            flash(f'Successfully created {created_count} user accounts')
        
        if error_count > 0:
            flash(f'Failed to create {error_count} user accounts')
            for error in result['errors']:
                flash(error)
        
        return redirect(url_for('user_management'))
    
    except Exception as e:
        flash(f'Error processing data: {str(e)}')
        return redirect(url_for('upload_users'))

@app.route('/admin/edit_user', methods=['POST'])
@login_required
def admin_edit_user():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    user_id = request.form['user_id']
    username = request.form['username']
    email = request.form['email']
    role = request.form['role']
    
    # Check if section_id is provided for student accounts
    if role == 'student' and not request.form.get('section_id'):
        flash('Section is required for student accounts')
        return redirect(url_for('user_management'))
    
    section_id = request.form.get('section_id') if role == 'student' else None
    password = request.form.get('password')
    
    user = User.query.get_or_404(user_id)
    
    # Check if username/email already exists (excluding current user)
    if User.query.filter(User.username == username, User.id != user_id).first():
        flash('Username already exists')
        return redirect(url_for('user_management'))
    
    if User.query.filter(User.email == email, User.id != user_id).first():
        flash('Email already exists')
        return redirect(url_for('user_management'))
    
    # Update user
    user.username = username
    user.email = email
    user.role = role
    user.section_id = int(section_id) if section_id else None
    
    if password:  # Only update password if provided
        user.password_hash = generate_password_hash(password)
    
    db.session.commit()
    
    flash(f'User {username} updated successfully')
    return redirect(url_for('user_management'))

@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get teacher's content
    lessons = Lesson.query.filter_by(teacher_id=current_user.id).all()
    quizzes = Quiz.query.filter_by(teacher_id=current_user.id).all()
    
    return render_template('teacher_dashboard.html', lessons=lessons, quizzes=quizzes)

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get available content filtered by student's section
    if current_user.section_id:
        lessons = Lesson.query.filter_by(is_published=True, section_id=current_user.section_id).all()
        quizzes = Quiz.query.filter_by(is_published=True, section_id=current_user.section_id).all()
    else:
        # If student has no section, show all content
        lessons = Lesson.query.filter_by(is_published=True).all()
        quizzes = Quiz.query.filter_by(is_published=True).all()
    
    # Get student's recent attempts
    recent_attempts = QuizAttempt.query.filter_by(student_id=current_user.id).order_by(QuizAttempt.completed_at.desc()).limit(5).all()
    
    return render_template('student_dashboard.html',
                         lessons=lessons,
                         quizzes=quizzes,
                         recent_attempts=recent_attempts)

# Lesson Routes
@app.route('/lessons')
@login_required
def lessons():
    if current_user.role == 'student':
        if current_user.section_id:
            lessons = Lesson.query.filter_by(is_published=True, section_id=current_user.section_id).all()
        else:
            lessons = Lesson.query.filter_by(is_published=True).all()
    else:
        lessons = Lesson.query.all()
    return render_template('lessons.html', lessons=lessons)

@app.route('/lesson/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Record student interaction
    if current_user.role == 'student':
        interaction = StudentInteraction(
            student_id=current_user.id,
            interaction_type='lesson_view',
            content_id=lesson_id
        )
        db.session.add(interaction)
        db.session.commit()
    
    return render_template('lesson_detail.html', lesson=lesson)

@app.route('/create_lesson', methods=['GET', 'POST'])
@login_required
def create_lesson():
    if current_user.role != 'teacher':
        flash('Access denied')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        section_id = request.form['section_id']
        file_path = None
        file_type = None
        
        # Handle file upload - this is now required
        if 'lesson_file' in request.files:
            file = request.files['lesson_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_type = filename.rsplit('.', 1)[1].lower()
                # Make path relative for storage
                file_path = file_path.replace('\\', '/')
            else:
                flash('Please upload a valid file')
                return redirect(url_for('create_lesson'))
        else:
            flash('File upload is required')
            return redirect(url_for('create_lesson'))
        
        lesson = Lesson(
            title=title,
            content=None,  # No content field needed
            content_type='file_upload',  # Always file upload
            file_path=file_path,
            file_type=file_type,
            section_id=int(section_id),
            teacher_id=current_user.id,
            is_published=True  # Always publish lessons
        )
        db.session.add(lesson)
        db.session.commit()
        flash('Lesson created successfully')
        return redirect(url_for('teacher_dashboard'))
    
    # Get all sections for the dropdown
    sections = Section.query.all()
    return render_template('create_lesson.html', sections=sections)

@app.route('/edit_lesson/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id):
    if current_user.role != 'teacher':
        flash('Access denied')
        return redirect(url_for('index'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Ensure the teacher owns this lesson
    if lesson.teacher_id != current_user.id:
        flash('Access denied - you can only edit your own lessons')
        return redirect(url_for('lessons'))
    
    if request.method == 'POST':
        # Update lesson details
        lesson.title = request.form['title']
        lesson.section_id = int(request.form['section_id'])
        lesson.is_published = request.form.get('is_published') == 'on'
        
        # Handle file upload if a new file is provided
        if 'lesson_file' in request.files:
            file = request.files['lesson_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_type = filename.rsplit('.', 1)[1].lower()
                # Make path relative for storage
                file_path = file_path.replace('\\', '/')
                
                # Update lesson with new file info
                lesson.file_path = file_path
                lesson.file_type = file_type
        
        db.session.commit()
        flash('Lesson updated successfully')
        return redirect(url_for('lessons'))
    
    # Get all sections for the dropdown
    sections = Section.query.all()
    return render_template('edit_lesson.html', lesson=lesson, sections=sections)

# Quiz Routes
@app.route('/quizzes')
@login_required
def quizzes():
    if current_user.role == 'student':
        if current_user.section_id:
            quizzes = Quiz.query.filter_by(is_published=True, section_id=current_user.section_id).all()
        else:
            quizzes = Quiz.query.filter_by(is_published=True).all()
    else:
        quizzes = Quiz.query.all()
    return render_template('quizzes.html', quizzes=quizzes)

@app.route('/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('take_quiz.html', quiz=quiz, questions=questions)

@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    if current_user.role != 'student':
        flash('Access denied')
        return redirect(url_for('index'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    # Validate that all questions have been answered
    for question in questions:
        answer = request.form.get(f'question_{question.id}')
        if not answer or answer.strip() == '':
            flash('Please answer all questions before submitting')
            return redirect(url_for('take_quiz', quiz_id=quiz_id))
    
    answers = {}
    score = 0
    total_points = 0
    
    for question in questions:
        answer = request.form.get(f'question_{question.id}')
        answers[str(question.id)] = answer
        total_points += question.points
        
        # Check if answer is correct
        if question.question_type == 'multiple_choice' or question.question_type == 'true_false':
            if answer and answer.strip() == question.correct_answer.strip():
                score += question.points
        elif question.question_type == 'short_answer':
            if answer and answer.lower().strip() == question.correct_answer.lower().strip():
                score += question.points
    
    # Save quiz attempt
    attempt = QuizAttempt(
        student_id=current_user.id,
        quiz_id=quiz_id,
        score=score,
        total_points=total_points,
        answers=json.dumps(answers)
    )
    db.session.add(attempt)
    
    # Record interaction
    interaction = StudentInteraction(
        student_id=current_user.id,
        interaction_type='quiz_attempt',
        content_id=quiz_id,
        performance_score=score/total_points if total_points > 0 else 0
    )
    db.session.add(interaction)
    
    db.session.commit()
    
    flash(f'Quiz completed! Your score: {score}/{total_points}')
    return redirect(url_for('student_dashboard'))

@app.route('/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if current_user.role != 'teacher':
        flash('Access denied')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        quiz = Quiz(
            title=request.form['title'],
            description=request.form['description'],
            section_id=int(request.form['section_id']),
            teacher_id=current_user.id,
            is_published=request.form.get('is_published') == 'on'
        )
        db.session.add(quiz)
        db.session.flush()  # Get the quiz ID
        
        # Add questions
        question_count = int(request.form.get('question_count', 0))
        for i in range(1, question_count + 1):  # Changed to start from 1 to match the UI
            # Skip questions that were removed
            if f'question_{i}_text' not in request.form:
                continue
                
            question_text = request.form.get(f'question_{i}_text')
            question_type = request.form.get(f'question_{i}_type')
            correct_answer = request.form.get(f'question_{i}_answer')
            points = int(request.form.get(f'question_{i}_points', 1))
            
            if question_text and correct_answer:
                options = None
                if question_type == 'multiple_choice':
                    options_list = []
                    # Get all options (could be more than 4 now)
                    j = 0
                    while f'question_{i}_option_{j}' in request.form:
                        option = request.form.get(f'question_{i}_option_{j}')
                        if option:
                            options_list.append(option)
                        j += 1
                    options = json.dumps(options_list)
                
                question = Question(
                    quiz_id=quiz.id,
                    question_text=question_text,
                    question_type=question_type,
                    options=options,
                    correct_answer=correct_answer,
                    points=points
                )
                db.session.add(question)
        
        db.session.commit()
        flash('Quiz created successfully')
        return redirect(url_for('teacher_dashboard'))
    
    # Get all sections for the dropdown
    sections = Section.query.all()
    return render_template('create_quiz.html', sections=sections)

@app.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    if current_user.role != 'teacher':
        flash('Access denied')
        return redirect(url_for('index'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Ensure the teacher owns this quiz
    if quiz.teacher_id != current_user.id:
        flash('Access denied - you can only edit your own quizzes')
        return redirect(url_for('quizzes'))
    
    if request.method == 'POST':
        # Update quiz details
        quiz.title = request.form['title']
        quiz.description = request.form['description']
        quiz.section_id = int(request.form['section_id'])
        quiz.is_published = request.form.get('is_published') == 'on'
        
        # Delete existing questions
        for question in quiz.questions:
            db.session.delete(question)
        
        # Add updated questions
        question_count = int(request.form.get('question_count', 0))
        for i in range(1, question_count + 1):  # Start from 1 to match the UI
            # Skip questions that were removed
            if f'question_{i}_text' not in request.form:
                continue
                
            question_text = request.form.get(f'question_{i}_text')
            question_type = request.form.get(f'question_{i}_type')
            correct_answer = request.form.get(f'question_{i}_answer')
            points = int(request.form.get(f'question_{i}_points', 1))
            
            if question_text and correct_answer:
                options = None
                if question_type == 'multiple_choice':
                    options_list = []
                    # Get all options (could be more than 4 now)
                    j = 0
                    while f'question_{i}_option_{j}' in request.form:
                        option = request.form.get(f'question_{i}_option_{j}')
                        if option:
                            options_list.append(option)
                        j += 1
                    options = json.dumps(options_list)
                
                question = Question(
                    quiz_id=quiz.id,
                    question_text=question_text,
                    question_type=question_type,
                    options=options,
                    correct_answer=correct_answer,
                    points=points
                )
                db.session.add(question)
        
        db.session.commit()
        flash('Quiz updated successfully')
        return redirect(url_for('quizzes'))
    
    # Get all sections for the dropdown
    sections = Section.query.all()
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    return render_template('edit_quiz.html', quiz=quiz, sections=sections, questions=questions)

@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    if current_user.role != 'teacher':
        flash('Access denied')
        return redirect(url_for('index'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Ensure the teacher owns this quiz
    if quiz.teacher_id != current_user.id:
        flash('Access denied - you can only delete your own quizzes')
        return redirect(url_for('quizzes'))
    
    # Delete the quiz (cascade will delete questions)
    db.session.delete(quiz)
    db.session.commit()
    
    flash('Quiz deleted successfully')
    return redirect(url_for('quizzes'))

@app.route('/delete_all_quizzes', methods=['POST'])
@login_required
def delete_all_quizzes():
    if current_user.role != 'teacher':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get all quizzes owned by the current teacher
    quizzes = Quiz.query.filter_by(teacher_id=current_user.id).all()
    
    # Delete all quizzes
    count = 0
    for quiz in quizzes:
        db.session.delete(quiz)
        count += 1
    
    db.session.commit()
    
    flash(f'Successfully deleted {count} quizzes')
    return redirect(url_for('quizzes'))

@app.route('/api/quiz_results/<int:quiz_id>')
@login_required
def quiz_results(quiz_id):
    if current_user.role != 'teacher':
        return jsonify({'error': 'Access denied'}), 403
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Ensure the teacher owns this quiz
    if quiz.teacher_id != current_user.id:
        return jsonify({'error': 'Access denied - you can only view results for your own quizzes'}), 403
    
    # Get all attempts for this quiz
    attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id).all()
    
    # Calculate statistics
    total_attempts = len(attempts)
    
    # Calculate passed/failed based on 50% threshold
    passed = 0
    failed = 0
    total_score_percentage = 0
    
    for attempt in attempts:
        score_percentage = (attempt.score / attempt.total_points * 100) if attempt.total_points > 0 else 0
        total_score_percentage += score_percentage
        
        if score_percentage >= 50:
            passed += 1
        else:
            failed += 1
    
    # Calculate average score
    average_score = round(total_score_percentage / total_attempts) if total_attempts > 0 else 0
    
    # Get recent attempts with student names
    recent_attempts = []
    for attempt in QuizAttempt.query.filter_by(quiz_id=quiz_id).order_by(QuizAttempt.completed_at.desc()).limit(10).all():
        student = User.query.get(attempt.student_id)
        score_percentage = round((attempt.score / attempt.total_points * 100)) if attempt.total_points > 0 else 0
        
        recent_attempts.append({
            'student_name': student.username,
            'score': attempt.score,
            'total_points': attempt.total_points,
            'score_percentage': score_percentage,
            'date': attempt.completed_at.strftime('%m/%d/%Y %H:%M')
        })
    
    return jsonify({
        'total_attempts': total_attempts,
        'passed': passed,
        'failed': failed,
        'average_score': average_score,
        'recent_attempts': recent_attempts
    })

# API Routes for AI Analytics
@app.route('/api/student_analytics/<int:student_id>')
@login_required
def student_analytics(student_id):
    if current_user.role not in ['admin', 'teacher']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get student interactions and quiz attempts
    interactions = StudentInteraction.query.filter_by(student_id=student_id).all()
    quiz_attempts = QuizAttempt.query.filter_by(student_id=student_id).all()
    
    # Use AI analytics for comprehensive analysis
    analytics_engine = get_analytics_instance()
    analysis = analytics_engine.analyze_student_performance(interactions, quiz_attempts)
    
    return jsonify(analysis)

@app.route('/admin/ai_analytics')
@login_required
def ai_analytics():
    if current_user.role not in ['admin', 'teacher']:
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get all students for the dropdown
    students = User.query.filter_by(role='student').all()
    
    return render_template('ai_analytics.html', students=students)

@app.route('/api/teacher_analytics')
@login_required
def teacher_analytics():
    if current_user.role not in ['admin', 'teacher']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get teacher statistics
    total_lessons = Lesson.query.count()
    total_quizzes = Quiz.query.count()
    
    # Find most active teacher
    teacher_lesson_counts = db.session.query(
        User.username,
        db.func.count(Lesson.id).label('lesson_count')
    ).join(Lesson, User.id == Lesson.teacher_id).group_by(User.id).all()
    
    most_active = max(teacher_lesson_counts, key=lambda x: x.lesson_count).username if teacher_lesson_counts else 'N/A'
    
    return jsonify({
        'total_lessons': total_lessons,
        'total_quizzes': total_quizzes,
        'most_active': most_active
    })

@app.route('/api/class_analytics')
@login_required
def class_analytics():
    if current_user.role not in ['admin', 'teacher']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get all students and their data
    students = User.query.filter_by(role='student').all()
    all_students_data = {}
    
    for student in students:
        interactions = StudentInteraction.query.filter_by(student_id=student.id).all()
        quiz_attempts = QuizAttempt.query.filter_by(student_id=student.id).all()
        all_students_data[student.id] = (interactions, quiz_attempts)
    
    # Use AI analytics for comprehensive class analysis
    analytics_engine = get_analytics_instance()
    analysis = analytics_engine.analyze_class_performance(all_students_data)
    
    return jsonify(analysis)

# Initialize database - moved to run.py for better control
# The @app.before_first_request decorator is deprecated in Flask 2.2+

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@school.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True)
