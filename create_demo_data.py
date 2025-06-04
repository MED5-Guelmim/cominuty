"""
Demo Data Creation Script for School Platform
Creates sample users, lessons, quizzes, and interactions for testing
"""

from app import app, db, User, Lesson, Quiz, Question, QuizAttempt, StudentInteraction
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import json
import random

def create_demo_data():
    """Create comprehensive demo data for the school platform"""
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create users
        print("Creating users...")
        
        # Admin user
        admin = User(
            username='admin',
            email='admin@school.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        
        # Teacher users
        teachers = [
            User(
                username='teacher1',
                email='teacher1@school.com',
                password_hash=generate_password_hash('teacher123'),
                role='teacher'
            ),
            User(
                username='teacher2',
                email='teacher2@school.com',
                password_hash=generate_password_hash('teacher123'),
                role='teacher'
            )
        ]
        
        for teacher in teachers:
            db.session.add(teacher)
        
        # Student users
        student_names = [
            'alice_student', 'bob_student', 'charlie_student', 'diana_student',
            'eve_student', 'frank_student', 'grace_student', 'henry_student',
            'iris_student', 'jack_student', 'kate_student', 'liam_student'
        ]
        
        students = []
        for name in student_names:
            student = User(
                username=name,
                email=f'{name}@school.com',
                password_hash=generate_password_hash('student123'),
                role='student'
            )
            students.append(student)
            db.session.add(student)
        
        db.session.commit()
        
        # Create lessons
        print("Creating lessons...")
        
        lessons_data = [
            {
                'title': 'Introduction to Mathematics',
                'content': '''<h3>Welcome to Mathematics</h3>
                <p>Mathematics is the study of numbers, shapes, and patterns. In this lesson, we will explore the fundamental concepts that form the foundation of mathematical thinking.</p>
                
                <h4>Learning Objectives:</h4>
                <ul>
                    <li>Understand basic mathematical concepts</li>
                    <li>Learn about numbers and operations</li>
                    <li>Explore geometric shapes</li>
                    <li>Recognize patterns in mathematics</li>
                </ul>
                
                <h4>Key Concepts:</h4>
                <p><b>Numbers:</b> Mathematics begins with numbers. We use numbers to count, measure, and describe quantities.</p>
                <p><b>Operations:</b> Addition, subtraction, multiplication, and division are the basic operations we perform with numbers.</p>
                <p><b>Geometry:</b> The study of shapes, sizes, and spatial relationships.</p>
                
                <h4>Practice Exercise:</h4>
                <p>Try solving these basic problems:</p>
                <ul>
                    <li>5 + 3 = ?</li>
                    <li>10 - 4 = ?</li>
                    <li>6 × 2 = ?</li>
                    <li>15 ÷ 3 = ?</li>
                </ul>''',
                'content_type': 'text',
                'teacher_id': teachers[0].id,
                'is_published': True
            },
            {
                'title': 'Basic Algebra Concepts',
                'content': '''<h3>Introduction to Algebra</h3>
                <p>Algebra is a branch of mathematics that uses letters and symbols to represent numbers and quantities in formulas and equations.</p>
                
                <h4>What is a Variable?</h4>
                <p>A variable is a letter (like x or y) that represents an unknown number. For example, in the equation x + 3 = 7, x is a variable that equals 4.</p>
                
                <h4>Basic Algebraic Operations:</h4>
                <ul>
                    <li><b>Addition:</b> x + 5</li>
                    <li><b>Subtraction:</b> x - 3</li>
                    <li><b>Multiplication:</b> 2x or 2 × x</li>
                    <li><b>Division:</b> x/4 or x ÷ 4</li>
                </ul>
                
                <h4>Solving Simple Equations:</h4>
                <p>To solve x + 3 = 7:</p>
                <ol>
                    <li>Subtract 3 from both sides: x + 3 - 3 = 7 - 3</li>
                    <li>Simplify: x = 4</li>
                </ol>''',
                'content_type': 'text',
                'teacher_id': teachers[0].id,
                'is_published': True
            },
            {
                'title': 'Introduction to Science',
                'content': '''<h3>What is Science?</h3>
                <p>Science is the systematic study of the natural world through observation, experimentation, and analysis.</p>
                
                <h4>Branches of Science:</h4>
                <ul>
                    <li><b>Physics:</b> The study of matter, energy, and motion</li>
                    <li><b>Chemistry:</b> The study of substances and their interactions</li>
                    <li><b>Biology:</b> The study of living organisms</li>
                    <li><b>Earth Science:</b> The study of Earth and its processes</li>
                </ul>
                
                <h4>The Scientific Method:</h4>
                <ol>
                    <li>Observation</li>
                    <li>Question</li>
                    <li>Hypothesis</li>
                    <li>Experiment</li>
                    <li>Analysis</li>
                    <li>Conclusion</li>
                </ol>
                
                <p>Science helps us understand how the world works and solve problems in our daily lives.</p>''',
                'content_type': 'text',
                'teacher_id': teachers[1].id,
                'is_published': True
            },
            {
                'title': 'History of Ancient Civilizations',
                'content': '''<h3>Ancient Civilizations</h3>
                <p>Ancient civilizations were complex societies that developed thousands of years ago and laid the foundation for modern culture.</p>
                
                <h4>Major Ancient Civilizations:</h4>
                
                <h5>1. Ancient Egypt (3100-30 BCE)</h5>
                <ul>
                    <li>Built pyramids and the Sphinx</li>
                    <li>Developed hieroglyphic writing</li>
                    <li>Advanced in medicine and mathematics</li>
                </ul>
                
                <h5>2. Ancient Greece (800-146 BCE)</h5>
                <ul>
                    <li>Birthplace of democracy</li>
                    <li>Great philosophers like Socrates, Plato, and Aristotle</li>
                    <li>Olympic Games originated here</li>
                </ul>
                
                <h5>3. Roman Empire (27 BCE-476 CE)</h5>
                <ul>
                    <li>Built extensive road networks</li>
                    <li>Advanced engineering and architecture</li>
                    <li>Spread Latin language and Roman law</li>
                </ul>
                
                <p>These civilizations contributed greatly to art, science, government, and culture that influence us today.</p>''',
                'content_type': 'text',
                'teacher_id': teachers[1].id,
                'is_published': True
            }
        ]
        
        lessons = []
        for lesson_data in lessons_data:
            lesson = Lesson(**lesson_data)
            lessons.append(lesson)
            db.session.add(lesson)
        
        db.session.commit()
        
        # Create quizzes with questions
        print("Creating quizzes...")
        
        # Math Quiz
        math_quiz = Quiz(
            title='Basic Mathematics Quiz',
            description='Test your understanding of basic mathematical concepts',
            teacher_id=teachers[0].id,
            is_published=True
        )
        db.session.add(math_quiz)
        db.session.flush()
        
        math_questions = [
            {
                'quiz_id': math_quiz.id,
                'question_text': 'What is 15 + 27?',
                'question_type': 'multiple_choice',
                'options': json.dumps(['40', '42', '45', '48']),
                'correct_answer': '42',
                'points': 2
            },
            {
                'quiz_id': math_quiz.id,
                'question_text': 'Is 17 a prime number?',
                'question_type': 'true_false',
                'options': None,
                'correct_answer': 'True',
                'points': 1
            },
            {
                'quiz_id': math_quiz.id,
                'question_text': 'What is the result of 8 × 7?',
                'question_type': 'short_answer',
                'options': None,
                'correct_answer': '56',
                'points': 2
            }
        ]
        
        for q_data in math_questions:
            question = Question(**q_data)
            db.session.add(question)
        
        # Science Quiz
        science_quiz = Quiz(
            title='Introduction to Science Quiz',
            description='Test your knowledge of basic scientific concepts',
            teacher_id=teachers[1].id,
            is_published=True
        )
        db.session.add(science_quiz)
        db.session.flush()
        
        science_questions = [
            {
                'quiz_id': science_quiz.id,
                'question_text': 'Which of the following is NOT a branch of science?',
                'question_type': 'multiple_choice',
                'options': json.dumps(['Physics', 'Chemistry', 'Literature', 'Biology']),
                'correct_answer': 'Literature',
                'points': 2
            },
            {
                'quiz_id': science_quiz.id,
                'question_text': 'The scientific method always starts with observation.',
                'question_type': 'true_false',
                'options': None,
                'correct_answer': 'True',
                'points': 1
            },
            {
                'quiz_id': science_quiz.id,
                'question_text': 'What is the first step in the scientific method?',
                'question_type': 'short_answer',
                'options': None,
                'correct_answer': 'observation',
                'points': 2
            }
        ]
        
        for q_data in science_questions:
            question = Question(**q_data)
            db.session.add(question)
        
        db.session.commit()
        
        # Create quiz attempts and interactions
        print("Creating quiz attempts and interactions...")
        
        quizzes = [math_quiz, science_quiz]
        
        for student in students:
            # Create lesson interactions
            for lesson in lessons:
                if random.random() < 0.8:  # 80% chance of viewing each lesson
                    interaction = StudentInteraction(
                        student_id=student.id,
                        interaction_type='lesson_view',
                        content_id=lesson.id,
                        duration=random.randint(120, 600),  # 2-10 minutes
                        timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                    )
                    db.session.add(interaction)
            
            # Create quiz attempts
            for quiz in quizzes:
                if random.random() < 0.7:  # 70% chance of taking each quiz
                    # Simulate different performance levels
                    performance_level = random.choice(['high', 'medium', 'low'])
                    
                    if performance_level == 'high':
                        score_percentage = random.uniform(0.8, 1.0)
                    elif performance_level == 'medium':
                        score_percentage = random.uniform(0.6, 0.8)
                    else:
                        score_percentage = random.uniform(0.3, 0.6)
                    
                    questions = Question.query.filter_by(quiz_id=quiz.id).all()
                    total_points = sum(q.points for q in questions)
                    score = int(total_points * score_percentage)
                    
                    # Create quiz attempt
                    attempt = QuizAttempt(
                        student_id=student.id,
                        quiz_id=quiz.id,
                        score=score,
                        total_points=total_points,
                        answers=json.dumps({}),  # Simplified for demo
                        completed_at=datetime.utcnow() - timedelta(days=random.randint(1, 20))
                    )
                    db.session.add(attempt)
                    
                    # Create corresponding interaction
                    interaction = StudentInteraction(
                        student_id=student.id,
                        interaction_type='quiz_attempt',
                        content_id=quiz.id,
                        duration=random.randint(300, 1200),  # 5-20 minutes
                        performance_score=score_percentage,
                        timestamp=attempt.completed_at
                    )
                    db.session.add(interaction)
        
        db.session.commit()
        
        print("Demo data created successfully!")
        print("\nLogin credentials:")
        print("Admin: admin / admin123")
        print("Teacher: teacher1 / teacher123 or teacher2 / teacher123")
        print("Student: alice_student / student123 (or any other student name)")
        print("\nTotal users created:")
        print(f"- 1 Admin")
        print(f"- 2 Teachers")
        print(f"- {len(students)} Students")
        print(f"- {len(lessons)} Lessons")
        print(f"- {len(quizzes)} Quizzes")

if __name__ == '__main__':
    create_demo_data()