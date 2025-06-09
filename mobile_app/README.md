# School Platform Mobile App

A React Native mobile application for the School Platform, providing access to lessons, quizzes, and educational content on mobile devices.

## Features

- **Cross-platform**: Works on both iOS and Android
- **Role-based access**: Different interfaces for students, teachers, and administrators
- **Secure authentication**: JWT-based authentication with secure token storage
- **Offline-ready**: Built with offline capabilities in mind
- **Material Design**: Modern UI using React Native Paper
- **Real-time sync**: Syncs with the web platform's database

## Prerequisites

Before you begin, ensure you have the following installed:

- Node.js (v16 or higher)
- npm or yarn
- Expo CLI (`npm install -g @expo/cli`)
- For iOS development: Xcode (macOS only)
- For Android development: Android Studio

## Installation

1. **Navigate to the mobile app directory:**
   ```bash
   cd mobile_app
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure the API endpoint:**
   
   Edit `src/context/AuthContext.js` and update the `API_BASE_URL`:
   ```javascript
   const API_BASE_URL = 'https://your-pythonanywhere-domain.com';
   ```

## Development

### Running the app

1. **Start the Expo development server:**
   ```bash
   npx expo start
   ```

2. **Run on device/simulator:**
   - **iOS**: Press `i` in the terminal or scan QR code with Camera app
   - **Android**: Press `a` in the terminal or scan QR code with Expo Go app
   - **Web**: Press `w` in the terminal

### Project Structure

```
mobile_app/
├── App.js                 # Main app component with navigation
├── package.json           # Dependencies and scripts
├── src/
│   ├── context/
│   │   └── AuthContext.js # Authentication context
│   └── screens/
│       ├── LoginScreen.js
│       ├── StudentDashboard.js
│       ├── TeacherDashboard.js
│       ├── AdminDashboard.js
│       ├── LessonsScreen.js
│       ├── LessonDetailScreen.js
│       ├── QuizzesScreen.js
│       ├── TakeQuizScreen.js
│       ├── CreateLessonScreen.js
│       ├── CreateQuizScreen.js
│       ├── ProfileScreen.js
│       └── AnalyticsScreen.js
└── README.md
```

## Backend Integration

The mobile app connects to the same Flask backend as the web application. Ensure your backend API includes the mobile endpoints defined in `api_mobile.py`.

### Required Backend Endpoints

- `POST /api/auth/login` - User authentication
- `GET /api/auth/verify` - Token verification
- `GET /api/dashboard/student` - Student dashboard data
- `GET /api/dashboard/teacher` - Teacher dashboard data
- `GET /api/dashboard/admin` - Admin dashboard data
- `GET /api/lessons` - Lessons listing
- `GET /api/lessons/<id>` - Lesson details
- `GET /api/quizzes` - Quizzes listing
- `GET /api/quizzes/<id>` - Quiz details

## Deployment

### Building for Production

1. **Configure app.json:**
   Update `app.json` with your app details:
   ```json
   {
     "expo": {
       "name": "School Platform",
       "slug": "school-platform",
       "version": "1.0.0",
       "platforms": ["ios", "android"],
       "icon": "./assets/icon.png",
       "splash": {
         "image": "./assets/splash.png"
       }
     }
   }
   ```

2. **Build for Android:**
   ```bash
   npx expo build:android
   ```

3. **Build for iOS:**
   ```bash
   npx expo build:ios
   ```

### Publishing to App Stores

1. **Google Play Store (Android):**
   - Download the APK from Expo
   - Upload to Google Play Console
   - Follow Google's publishing guidelines

2. **Apple App Store (iOS):**
   - Download the IPA from Expo
   - Upload using Xcode or Application Loader
   - Follow Apple's App Store guidelines

## Configuration

### Environment Variables

Create a `.env` file in the mobile app directory:

```env
API_BASE_URL=https://your-pythonanywhere-domain.com
APP_NAME=School Platform
```

### Customization

1. **Colors and Themes:**
   - Modify the theme in `App.js`
   - Update colors in individual screen styles

2. **App Icon and Splash Screen:**
   - Replace `assets/icon.png` with your app icon
   - Replace `assets/splash.png` with your splash screen

3. **App Name and Metadata:**
   - Update `app.json` with your app details
   - Modify `package.json` name and description

## Demo Credentials

For testing purposes, use these demo credentials:

- **Admin**: `admin` / `admin123`
- **Teacher**: `teacher1` / `teacher123`
- **Student**: `alice_student` / `student123`

## Troubleshooting

### Common Issues

1. **Metro bundler issues:**
   ```bash
   npx expo start --clear
   ```

2. **iOS simulator not opening:**
   - Ensure Xcode is installed
   - Check iOS simulator is available

3. **Android emulator issues:**
   - Ensure Android Studio is installed
   - Start an Android Virtual Device (AVD)

4. **Network connectivity:**
   - Check API endpoint URL
   - Ensure backend server is running
   - Verify CORS settings on backend

### Performance Optimization

1. **Enable Hermes (Android):**
   Add to `app.json`:
   ```json
   {
     "expo": {
       "android": {
         "jsEngine": "hermes"
       }
     }
   }
   ```

2. **Optimize images:**
   - Use appropriate image sizes
   - Consider using WebP format

3. **Bundle size optimization:**
   - Remove unused dependencies
   - Use dynamic imports where possible

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on both platforms
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review Expo documentation: https://docs.expo.dev/
- React Native documentation: https://reactnative.dev/docs/getting-started
