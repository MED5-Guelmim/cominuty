from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json
import jwt
from functools import wraps

# Import existing models and configurations
from app import db, User, Section, Lesson, Quiz, Question, QuizAttempt, StudentInteraction, Competition
from config import Config

# Initialize Flask app for mobile API
api_app = Flask(__name__)
api_app.config.from_object(Config)

# Enable CORS for mobile app
CORS(api_app, origins=["*"])

# Initialize extensions
db.init_app(api_app)

# JWT Configuration
JWT_SECRET = api_app.config['SECRET_KEY']
JWT_EXPIRATION_DELTA = timedelta(days=7)

def generate_token(user_id):
    """Generate JWT token for user authentication"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def role_required(roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

# Authentication Routes
@api_app.route('/api/auth/login', methods=['POST'])
def login():
    """Mobile login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        token = generate_token(user.id)
        
        # Get section info if user is a student
        section_info = None
        if user.section_id:
            section = Section.query.get(user.section_id)
            section_info = {
                'id': section.id,
                'name': section.name,
                'description': section.description
            } if section else None
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'section': section_info,
                'created_at': user.created_at.isoformat()
            }
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@api_app.route('/api/auth/verify', methods=['GET'])
@token_required
def verify_token_endpoint(current_user):
    """Verify token and return user info"""
    section_info = None
    if current_user.section_id:
        section = Section.query.get(current_user.section_id)
        section_info = {
            'id': section.id,
            'name': section.name,
            'description': section.description
        } if section else None
    
    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'role': current_user.role,
            'section': section_info,
            'created_at': current_user.created_at.isoformat()
        }
    }), 200

# Dashboard Routes
@api_app.route('/api/dashboard/student', methods=['GET'])
@token_required
@role_required(['student'])
def student_dashboard(current_user):
    """Get student dashboard data"""
    # Get available content filtered by student's section
    if current_user.section_id:
        lessons = Lesson.query.filter_by(is_published=True, section_id=current_user.section_id).all()
        quizzes = Quiz.query.filter_by(is_published=True, section_id=current_user.section_id).all()
    else:
        lessons = Lesson.query.filter_by(is_published=True).all()
        quizzes = Quiz.query.filter_by(is_published=True).all()
    
    # Get recent quiz attempts
    recent_attempts = QuizAttempt.query.filter_by(student_id=current_user.id)\
        .order_by(QuizAttempt.completed_at.desc()).limit(5).all()
    
    # Format lessons
    lessons_data = []
    for lesson in lessons:
        teacher = User.query.get(lesson.teacher_id)
        lessons_data.append({
            'id': lesson.id,
            'title': lesson.title,
            'teacher': teacher.username if teacher else 'Unknown',
            'created_at': lesson.created_at.isoformat(),
            'file_type': lesson.file_type
        })
    
    # Format quizzes
    quizzes_data = []
    for quiz in quizzes:
        teacher = User.query.get(quiz.teacher_id)
        # Check if student has attempted this quiz
        attempt = QuizAttempt.query.filter_by(student_id=current_user.id, quiz_id=quiz.id).first()
        quizzes_data.append({
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'teacher': teacher.username if teacher else 'Unknown',
            'created_at': quiz.created_at.isoformat(),
            'attempted': attempt is not None,
            'score': f"{attempt.score}/{attempt.total_points}" if attempt else None
        })
    
    # Format recent attempts
    attempts_data = []
    for attempt in recent_attempts:
        quiz = Quiz.query.get(attempt.quiz_id)
        attempts_data.append({
            'quiz_title': quiz.title if quiz else 'Unknown',
            'score': attempt.score,
            'total_points': attempt.total_points,
            'percentage': round((attempt.score / attempt.total_points) * 100) if attempt.total_points > 0 else 0,
            'completed_at': attempt.completed_at.isoformat()
        })
    
    return jsonify({
        'lessons': lessons_data,
        'quizzes': quizzes_data,
        'recent_attempts': attempts_data,
        'stats': {
            'total_lessons': len(lessons_data),
            'total_quizzes': len(quizzes_data),
            'completed_quizzes': len([q for q in quizzes_data if q['attempted']])
        }
    }), 200

@api_app.route('/api/dashboard/teacher', methods=['GET'])
@token_required
@role_required(['teacher'])
def teacher_dashboard(current_user):
    """Get teacher dashboard data"""
    # Get teacher's content
    lessons = Lesson.query.filter_by(teacher_id=current_user.id).all()
    quizzes = Quiz.query.filter_by(teacher_id=current_user.id).all()
    
    # Get quiz attempts for teacher's quizzes
    quiz_ids = [quiz.id for quiz in quizzes]
    total_attempts = QuizAttempt.query.filter(QuizAttempt.quiz_id.in_(quiz_ids)).count()
    
    # Format lessons
    lessons_data = []
    for lesson in lessons:
        section = Section.query.get(lesson.section_id)
        lessons_data.append({
            'id': lesson.id,
            'title': lesson.title,
            'section': section.name if section else 'No Section',
            'created_at': lesson.created_at.isoformat(),
            'is_published': lesson.is_published,
            'file_type': lesson.file_type
        })
    
    # Format quizzes
    quizzes_data = []
    for quiz in quizzes:
        section = Section.query.get(quiz.section_id)
        attempts_count = QuizAttempt.query.filter_by(quiz_id=quiz.id).count()
        questions_count = Question.query.filter_by(quiz_id=quiz.id).count()
        
        quizzes_data.append({
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'section': section.name if section else 'No Section',
            'created_at': quiz.created_at.isoformat(),
            'is_published': quiz.is_published,
            'questions_count': questions_count,
            'attempts_count': attempts_count
        })
    
    return jsonify({
        'lessons': lessons_data,
        'quizzes': quizzes_data,
        'stats': {
            'total_lessons': len(lessons_data),
            'total_quizzes': len(quizzes_data),
            'total_attempts': total_attempts,
            'published_lessons': len([l for l in lessons_data if l['is_published']]),
            'published_quizzes': len([q for q in quizzes_data if q['is_published']])
        }
    }), 200

@api_app.route('/api/dashboard/admin', methods=['GET'])
@token_required
@role_required(['admin'])
def admin_dashboard(current_user):
    """Get admin dashboard data"""
    # Get statistics
    total_users = User.query.count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_students = User.query.filter_by(role='student').count()
    total_lessons = Lesson.query.count()
    total_quizzes = Quiz.query.count()
    total_sections = Section.query.count()
    
    # Get recent activities
    recent_activities = []
    
    # Recent quiz attempts
    quiz_attempts = QuizAttempt.query.order_by(QuizAttempt.completed_at.desc()).limit(5).all()
    for attempt in quiz_attempts:
        student = User.query.get(attempt.student_id)
        quiz = Quiz.query.get(attempt.quiz_id)
        if student and quiz:
            recent_activities.append({
                'time': attempt.completed_at.isoformat(),
                'user': student.username,
                'action': 'quiz_completed',
                'details': f"{quiz.title} - Score: {int((attempt.score / attempt.total_points) * 100)}%"
            })
    
    # Recent lessons
    lessons = Lesson.query.order_by(Lesson.created_at.desc()).limit(5).all()
    for lesson in lessons:
        teacher = User.query.get(lesson.teacher_id)
        if teacher:
            recent_activities.append({
                'time': lesson.created_at.isoformat(),
                'user': teacher.username,
                'action': 'lesson_created',
                'details': lesson.title
            })
    
    # Sort activities by time
    recent_activities.sort(key=lambda x: x['time'], reverse=True)
    recent_activities = recent_activities[:10]
    
    return jsonify({
        'stats': {
            'total_users': total_users,
            'total_teachers': total_teachers,
            'total_students': total_students,
            'total_lessons': total_lessons,
            'total_quizzes': total_quizzes,
            'total_sections': total_sections
        },
        'recent_activities': recent_activities
    }), 200

# Lessons Routes
@api_app.route('/api/lessons', methods=['GET'])
@token_required
def get_lessons(current_user):
    """Get lessons based on user role"""
    if current_user.role == 'student':
        if current_user.section_id:
            lessons = Lesson.query.filter_by(is_published=True, section_id=current_user.section_id).all()
        else:
            lessons = Lesson.query.filter_by(is_published=True).all()
    elif current_user.role == 'teacher':
        lessons = Lesson.query.filter_by(teacher_id=current_user.id).all()
    else:  # admin
        lessons = Lesson.query.all()
    
    lessons_data = []
    for lesson in lessons:
        teacher = User.query.get(lesson.teacher_id)
        section = Section.query.get(lesson.section_id)
        lessons_data.append({
            'id': lesson.id,
            'title': lesson.title,
            'teacher': teacher.username if teacher else 'Unknown',
            'section': section.name if section else 'No Section',
            'created_at': lesson.created_at.isoformat(),
            'is_published': lesson.is_published,
            'file_type': lesson.file_type,
            'file_path': lesson.file_path
        })
    
    return jsonify({'lessons': lessons_data}), 200

@api_app.route('/api/lessons/<int:lesson_id>', methods=['GET'])
@token_required
def get_lesson_detail(current_user, lesson_id):
    """Get lesson details"""
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Check access permissions
    if current_user.role == 'student':
        if not lesson.is_published:
            return jsonify({'error': 'Lesson not available'}), 403
        if current_user.section_id and lesson.section_id != current_user.section_id:
            return jsonify({'error': 'Access denied'}), 403
    elif current_user.role == 'teacher' and lesson.teacher_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Record student interaction
    if current_user.role == 'student':
        interaction = StudentInteraction(
            student_id=current_user.id,
            interaction_type='lesson_view',
            content_id=lesson_id,
            timestamp=datetime.utcnow()
        )
        db.session.add(interaction)
        db.session.commit()
    
    teacher = User.query.get(lesson.teacher_id)
    section = Section.query.get(lesson.section_id)
    
    return jsonify({
        'id': lesson.id,
        'title': lesson.title,
        'content': lesson.content,
        'content_type': lesson.content_type,
        'file_path': lesson.file_path,
        'file_type': lesson.file_type,
        'teacher': teacher.username if teacher else 'Unknown',
        'section': section.name if section else 'No Section',
        'created_at': lesson.created_at.isoformat(),
        'is_published': lesson.is_published
    }), 200

# Quizzes Routes
@api_app.route('/api/quizzes', methods=['GET'])
@token_required
def get_quizzes(current_user):
    """Get quizzes based on user role"""
    if current_user.role == 'student':
        if current_user.section_id:
            quizzes = Quiz.query.filter_by(is_published=True, section_id=current_user.section_id).all()
        else:
            quizzes = Quiz.query.filter_by(is_published=True).all()
    elif current_user.role == 'teacher':
        quizzes = Quiz.query.filter_by(teacher_id=current_user.id).all()
    else:  # admin
        quizzes = Quiz.query.all()
    
    quizzes_data = []
    for quiz in quizzes:
        teacher = User.query.get(quiz.teacher_id)
        section = Section.query.get(quiz.section_id)
        questions_count = Question.query.filter_by(quiz_id=quiz.id).count()
        
        # Check if student has attempted this quiz
        attempted = False
        score_info = None
        if current_user.role == 'student':
            attempt = QuizAttempt.query.filter_by(student_id=current_user.id, quiz_id=quiz.id).first()
            attempted = attempt is not None
            if attempt:
                score_info = {
                    'score': attempt.score,
                    'total_points': attempt.total_points,
                    'percentage': round((attempt.score / attempt.total_points) * 100) if attempt.total_points > 0 else 0,
                    'completed_at': attempt.completed_at.isoformat()
                }
        
        quizzes_data.append({
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'teacher': teacher.username if teacher else 'Unknown',
            'section': section.name if section else 'No Section',
            'created_at': quiz.created_at.isoformat(),
            'is_published': quiz.is_published,
            'questions_count': questions_count,
            'attempted': attempted,
            'score_info': score_info
        })
    
    return jsonify({'quizzes': quizzes_data}), 200

@api_app.route('/api/quizzes/<int:quiz_id>', methods=['GET'])
@token_required
def get_quiz_detail(current_user, quiz_id):
    """Get quiz details with questions"""
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check access permissions
    if current_user.role == 'student':
        if not quiz.is_published:
            return jsonify({'error': 'Quiz not available'}), 403
        if current_user.section_id and quiz.section_id != current_user.section_id:
            return jsonify({'error': 'Access denied'}), 403
    elif current_user.role == 'teacher' and quiz.teacher_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    teacher = User.query.get(quiz.teacher_id)
    section = Section.query.get(quiz.section_id)
    
    questions_data = []
    for question in questions:
        question_data = {
            'id': question.id,
            'question_text': question.question_text,
            'question_type': question.question_type,
            'points': question.points
        }
        
        # Add options for multiple choice questions
        if question.question_type == 'multiple_choice' and question.options:
            try:
                question_data['options'] = json.loads(question.options)
            except:
                question_data['options'] = []
        
        # Don't include correct answer for students
        if current_user.role != 'student':
            question_data['correct_answer'] = question.correct_answer
        
        questions_data.append(question_data)
    
    return jsonify({
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'teacher': teacher.username if teacher else 'Unknown',
        'section': section.name if section else 'No Section',
        'created_at': quiz.created_at.isoformat(),
        'is_published': quiz.is_published,
        'questions': questions_data
    }), 200

@api_app.route('/api/quizzes/<int:quiz_id>/submit', methods=['POST'])
@token_required
@role_required(['student'])
def submit_quiz(current_user, quiz_id):
    """Submit quiz answers"""
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check access permissions
    if not quiz.is_published:
        return jsonify({'error': 'Quiz not available'}), 403
    if current_user.section_id and quiz.section_id != current_user.section_id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    answers = data.get('answers', {})
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    # Validate that all questions have been answered
    for question in questions:
        if str(question.id) not in answers:
            return jsonify({'error': f'Question {question.id} not answered'}), 400
    
    score = 0
    total_points = 0
    
    for question in questions:
        answer = answers.get(str(question.id), '')
        total_points += question.points
        
        # Check if answer is correct
        if question.question_type in ['multiple_choice', 'true_false']:
            if answer.strip() == question.correct_answer.strip():
                score += question.points
        elif question.question_type == 'short_answer':
            if answer.lower().strip() == question.correct_answer.lower().strip():
                score += question.points
    
    # Save quiz attempt
    attempt = QuizAttempt(
        student_id=current_user.id,
        quiz_id=quiz_id,
        score=score,
        total_points=total_points,
        answers=json.dumps(answers),
        completed_at=datetime.utcnow()
    )
    db.session.add(attempt)
    
    # Record interaction
    interaction = StudentInteraction(
        student_id=current_user.id,
        interaction_type='quiz_attempt',
        content_id=quiz_id,
        performance_score=score/total_points if total_points > 0 else 0,
        timestamp=datetime.utcnow()
    )
    db.session.add(interaction)
    db.session.commit()
    
    percentage = round((score / total_points) * 100) if total_points > 0 else 0
    
    return jsonify({
        'success': True,
        'score': score,
        'total_points': total_points,
        'percentage': percentage,
        'message': f'Quiz completed! Your score: {score}/{total_points} ({percentage}%)'
    }), 200

# Sections Routes
@api_app.route('/api/sections', methods=['GET'])
@token_required
def get_sections(current_user):
    """Get all sections"""
    sections = Section.query.all()
    sections_data = []
    for section in sections:
        sections_data.append({
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'created_at': section.created_at.isoformat()
        })
    
    return jsonify({'sections': sections_data}), 200

# Analytics Routes
@api_app.route('/api/analytics/student/<int:student_id>', methods=['GET'])
@token_required
@role_required(['admin', 'teacher'])
def get_student_analytics(current_user, student_id):
    """Get analytics for a specific student"""
    student = User.query.get_or_404(student_id)
    
    # Get student interactions and quiz attempts
    interactions = StudentInteraction.query.filter_by(student_id=student_id).all()
    quiz_attempts = QuizAttempt.query.filter_by(student_id=student_id).all()
    
    # Calculate basic statistics
    total_lessons_viewed = len([i for i in interactions if i.interaction_type == 'lesson_view'])
    total_quizzes_taken = len(quiz_attempts)
    
    # Calculate average score
    if quiz_attempts:
        total_score = sum(attempt.score for attempt in quiz_attempts)
        total_possible = sum(attempt.total_points for attempt in quiz_attempts)
        average_percentage = round((total_score / total_possible) * 100) if total_possible > 0 else 0
    else:
        average_percentage = 0
    
    # Recent activity
    recent_attempts = quiz_attempts[-5:] if len(quiz_attempts) > 5 else quiz_attempts
    recent_attempts_data = []
    for attempt in recent_attempts:
        quiz = Quiz.query.get(attempt.quiz_id)
        recent_attempts_data.append({
            'quiz_title': quiz.title if quiz else 'Unknown',
            'score': attempt.score,
            'total_points': attempt.total_points,
            'percentage': round((attempt.score / attempt.total_points) * 100) if attempt.total_points > 0 else 0,
            'completed_at': attempt.completed_at.isoformat()
        })
    
    return jsonify({
        'student': {
            'id': student.id,
            'username': student.username,
            'email': student.email
        },
        'stats': {
            'lessons_viewed': total_lessons_viewed,
            'quizzes_taken': total_quizzes_taken,
            'average_score': average_percentage
        },
        'recent_attempts': recent_attempts_data
    }), 200

# File serving route for lesson files
@api_app.route('/api/files/<path:filename>')
@token_required
def serve_file(current_user, filename):
    """Serve uploaded files"""
    from flask import send_from_directory
    return send_from_directory('static/uploads', filename)

if __name__ == '__main__':
    with api_app.app_context():
        db.create_all()
    api_app.run(debug=True, port=5001)
