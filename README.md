# School Platform - Full-Stack Educational System

A comprehensive educational platform designed for secondary schools, featuring interactive lessons, quizzes, competitions, and AI-powered analytics to enhance the learning experience.

## Features

### 🎓 User Roles & Permissions
- **Administrators**: Manage teacher accounts, monitor platform activity, view AI analytics
- **Teachers**: Create lessons and quizzes, view student performance, manage content
- **Students**: Access lessons, take quizzes, participate in competitions, track progress

### 📚 Core Functionality
- **Interactive Lessons**: Support for text, video, image, and PDF content
- **Smart Quizzes**: Multiple choice, true/false, and short answer questions with automatic grading
- **AI Analytics**: Advanced student performance tracking and learning pattern analysis
- **Progress Tracking**: Real-time monitoring of student engagement and achievement
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices

### 🤖 AI-Powered Features
- Student performance analysis and predictions
- Learning pattern recognition
- Personalized recommendations
- Class-wide analytics and insights
- At-risk student identification
- Engagement scoring

## Technology Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **Flask-Login** - User authentication
- **SQLite** - Database (easily replaceable with PostgreSQL/MySQL)

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with custom properties
- **JavaScript (ES6+)** - Interactive functionality
- **Bootstrap 5** - Responsive UI framework
- **Chart.js** - Data visualization
- **Font Awesome** - Icons

### AI/Analytics
- **Pandas** - Data manipulation and analysis
- **Scikit-learn** - Machine learning algorithms
- **NumPy** - Numerical computing

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd school-platform
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python create_demo_data.py
```

### 5. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Demo Accounts

After running the demo data script, you can log in with these accounts:

### Administrator
- **Username**: `admin`
- **Password**: `admin123`

### Teachers
- **Username**: `teacher1` or `teacher2`
- **Password**: `teacher123`

### Students
- **Username**: `alice_student`, `bob_student`, etc.
- **Password**: `student123`

## Project Structure

```
school-platform/
├── app.py                 # Main Flask application
├── ai_analytics.py        # AI analytics engine
├── create_demo_data.py    # Demo data creation script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── main.js       # JavaScript functionality
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── index.html        # Homepage
    ├── login.html        # Login page
    ├── register.html     # Registration page
    ├── admin_dashboard.html
    ├── teacher_dashboard.html
    ├── student_dashboard.html
    ├── lessons.html
    ├── lesson_detail.html
    ├── create_lesson.html
    ├── quizzes.html
    ├── take_quiz.html
    └── create_quiz.html
```

## Usage Guide

### For Administrators
1. **Dashboard Overview**: View platform statistics and user analytics
2. **User Management**: Monitor teacher and student accounts
3. **AI Insights**: Access comprehensive analytics and performance reports
4. **System Monitoring**: Track platform usage and engagement

### For Teachers
1. **Create Lessons**: 
   - Add multimedia content (text, video, images, PDFs)
   - Use rich text formatting
   - Publish or save as drafts
2. **Create Quizzes**:
   - Add multiple question types
   - Set point values
   - Configure automatic grading
3. **Monitor Students**:
   - View individual student performance
   - Access class-wide analytics
   - Identify students needing support

### For Students
1. **Access Lessons**: Browse and study available content
2. **Take Quizzes**: Complete assessments with instant feedback
3. **Track Progress**: Monitor your learning journey and achievements
4. **View Performance**: See detailed analytics of your progress

## API Endpoints

### Analytics APIs
- `GET /api/student_analytics/<student_id>` - Individual student analysis
- `GET /api/class_analytics` - Class-wide performance analysis

### Content APIs
- `GET /lessons` - List all lessons
- `GET /lesson/<lesson_id>` - View specific lesson
- `GET /quizzes` - List all quizzes
- `GET /quiz/<quiz_id>` - Take specific quiz
- `POST /submit_quiz/<quiz_id>` - Submit quiz answers

## AI Analytics Features

### Student Analysis
- **Performance Metrics**: Average scores, improvement rates, difficulty areas
- **Learning Patterns**: Preferred study times, session duration, content preferences
- **Engagement Scoring**: Comprehensive engagement measurement (0-100)
- **Progress Prediction**: AI-powered future performance predictions
- **Personalized Recommendations**: Tailored suggestions for improvement

### Class Analysis
- **Performance Distribution**: Grade distribution across the class
- **Student Grouping**: AI-powered clustering of students by performance patterns
- **At-Risk Identification**: Early warning system for struggling students
- **Engagement Insights**: Class-wide engagement patterns and trends

## Customization

### Adding New Question Types
1. Update the `Question` model in `app.py`
2. Modify quiz creation templates
3. Update grading logic in `submit_quiz` route

### Extending AI Analytics
1. Add new analysis methods to `ai_analytics.py`
2. Create corresponding API endpoints
3. Update dashboard templates to display new insights

### Styling Customization
- Modify `static/css/style.css` for visual changes
- Update CSS custom properties for theme colors
- Add new animations and transitions

## Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Flask-Login for secure user sessions
- **Role-Based Access**: Strict permission controls for different user types
- **Input Validation**: Form validation and sanitization
- **CSRF Protection**: Built-in protection against cross-site request forgery

## Performance Optimization

- **Database Indexing**: Optimized queries for better performance
- **Caching**: Browser caching for static assets
- **Lazy Loading**: Efficient data loading strategies
- **Responsive Images**: Optimized media delivery

## Deployment

### Production Considerations
1. **Database**: Replace SQLite with PostgreSQL or MySQL
2. **Web Server**: Use Gunicorn with Nginx
3. **Environment Variables**: Secure configuration management
4. **SSL/HTTPS**: Enable secure connections
5. **Monitoring**: Add logging and error tracking

### Environment Variables
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export DATABASE_URL=your-database-url
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the demo data and examples

## Future Enhancements

- **Real-time Notifications**: WebSocket-based live updates
- **Mobile App**: Native mobile applications
- **Advanced Analytics**: More sophisticated AI models
- **Gamification**: Badges, leaderboards, and achievements
- **Video Conferencing**: Integrated virtual classrooms
- **Assignment System**: File upload and submission features
- **Parent Portal**: Parent access to student progress
- **Multi-language Support**: Internationalization features

---

Built with ❤️ for education and learning.