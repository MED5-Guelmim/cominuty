# Mobile App Deployment Guide

This guide provides step-by-step instructions for deploying the School Platform mobile application alongside your existing web application on PythonAnywhere.

## Overview

The mobile application has been created as a React Native app using Expo, which connects to your existing Flask backend. The mobile app shares the same database and authentication system as your web application.

## Files Created

### Backend API Extension
- `api_mobile.py` - Mobile-specific API endpoints
- `requirements_mobile.txt` - Additional Python dependencies for mobile API

### Mobile Application
- `mobile_app/` - Complete React Native application
- `mobile_app/package.json` - Mobile app dependencies
- `mobile_app/App.js` - Main application with navigation
- `mobile_app/src/context/AuthContext.js` - Authentication management
- `mobile_app/src/screens/` - All application screens
- `mobile_app/README.md` - Mobile app documentation

## Step 1: Backend Setup on PythonAnywhere

### 1.1 Update Flask Application

Add the mobile API to your existing Flask app by modifying your main `app.py`:

```python
# Add this import at the top of your app.py
from api_mobile import mobile_api

# Register the mobile API blueprint
app.register_blueprint(mobile_api, url_prefix='/api')
```

### 1.2 Install Additional Dependencies

Upload `requirements_mobile.txt` to your PythonAnywhere files and install the new dependencies:

```bash
# In your PythonAnywhere console
pip3.10 install --user -r requirements_mobile.txt
```

### 1.3 Update CORS Settings

Ensure your Flask app allows CORS for mobile requests. If you don't have CORS configured, add this to your `app.py`:

```python
from flask_cors import CORS

# Add after creating your Flask app
CORS(app, origins=['*'])  # Configure appropriately for production
```

### 1.4 Restart Your Web App

In your PythonAnywhere dashboard:
1. Go to the "Web" tab
2. Click "Reload" to restart your web application

## Step 2: Mobile App Development Setup

### 2.1 Local Development Environment

On your local machine:

```bash
# Navigate to the mobile app directory
cd mobile_app

# Install dependencies
npm install

# Install Expo CLI globally if not already installed
npm install -g @expo/cli

# Start the development server
npx expo start
```

### 2.2 Configure API Endpoint

Edit `mobile_app/src/context/AuthContext.js` and update the API URL:

```javascript
const API_BASE_URL = 'https://yourusername.pythonanywhere.com';
```

Replace `yourusername` with your actual PythonAnywhere username.

### 2.3 Test the Connection

1. Start the Expo development server
2. Open the app on your device using Expo Go
3. Try logging in with the demo credentials:
   - Admin: `admin` / `admin123`
   - Teacher: `teacher1` / `teacher123`
   - Student: `alice_student` / `student123`

## Step 3: Mobile App Deployment

### 3.1 Prepare for Production

1. **Update app.json** with your app details:
```json
{
  "expo": {
    "name": "Your School Platform",
    "slug": "your-school-platform",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "platforms": ["ios", "android"],
    "android": {
      "package": "com.yourcompany.schoolplatform"
    },
    "ios": {
      "bundleIdentifier": "com.yourcompany.schoolplatform"
    }
  }
}
```

2. **Create app icons and splash screens** (optional but recommended):
   - Icon: 1024x1024 PNG
   - Splash: 1242x2436 PNG

### 3.2 Build for Android

```bash
# Build APK for Android
npx expo build:android

# Or build AAB (recommended for Play Store)
npx expo build:android --type app-bundle
```

### 3.3 Build for iOS

```bash
# Build for iOS (requires Apple Developer account)
npx expo build:ios
```

### 3.4 Alternative: Expo Application Services (EAS)

For more advanced builds, consider using EAS Build:

```bash
# Install EAS CLI
npm install -g @expo/eas-cli

# Configure EAS
eas build:configure

# Build for both platforms
eas build --platform all
```

## Step 4: App Store Deployment

### 4.1 Google Play Store (Android)

1. Create a Google Play Developer account ($25 one-time fee)
2. Download your APK/AAB from Expo
3. Upload to Google Play Console
4. Fill in app details, screenshots, and descriptions
5. Submit for review

### 4.2 Apple App Store (iOS)

1. Create an Apple Developer account ($99/year)
2. Download your IPA from Expo
3. Upload using Xcode or Application Loader
4. Create app listing in App Store Connect
5. Submit for review

## Step 5: Testing and Quality Assurance

### 5.1 Test Scenarios

Test the following functionality:
- [ ] User login/logout
- [ ] Student dashboard loading
- [ ] Teacher dashboard loading
- [ ] Admin dashboard loading
- [ ] Lessons listing
- [ ] Quizzes listing
- [ ] Navigation between screens
- [ ] Network error handling
- [ ] Offline behavior

### 5.2 Device Testing

Test on various devices:
- [ ] Different Android versions
- [ ] Different iOS versions
- [ ] Various screen sizes
- [ ] Different network conditions

## Step 6: Maintenance and Updates

### 6.1 Over-the-Air Updates

Expo supports OTA updates for JavaScript changes:

```bash
# Publish an update
npx expo publish
```

### 6.2 App Store Updates

For native changes or major updates:
1. Update version in `app.json`
2. Build new version
3. Submit to app stores

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure CORS is properly configured on your Flask backend
   - Check that your API endpoints are accessible

2. **Authentication Issues**
   - Verify JWT secret keys match between web and mobile
   - Check token expiration settings

3. **Build Failures**
   - Clear Expo cache: `npx expo start --clear`
   - Check for dependency conflicts
   - Ensure all required assets are present

4. **Network Issues**
   - Test API endpoints directly in browser
   - Check PythonAnywhere logs for errors
   - Verify SSL certificate is valid

### Getting Help

- Expo Documentation: https://docs.expo.dev/
- React Native Documentation: https://reactnative.dev/
- PythonAnywhere Help: https://help.pythonanywhere.com/

## Security Considerations

1. **API Security**
   - Use HTTPS only in production
   - Implement proper rate limiting
   - Validate all input data

2. **Authentication**
   - Use secure JWT secrets
   - Implement token refresh mechanism
   - Store tokens securely on device

3. **Data Protection**
   - Encrypt sensitive data
   - Follow platform security guidelines
   - Regular security audits

## Performance Optimization

1. **Backend**
   - Implement caching for frequently accessed data
   - Optimize database queries
   - Use pagination for large datasets

2. **Mobile App**
   - Implement lazy loading
   - Optimize images and assets
   - Use React Native performance best practices

## Next Steps

1. **Enhanced Features**
   - Push notifications
   - Offline data synchronization
   - File upload/download
   - Real-time messaging

2. **Analytics**
   - User behavior tracking
   - Performance monitoring
   - Crash reporting

3. **Monetization**
   - In-app purchases
   - Subscription models
   - Advertisement integration

## Support

For technical support:
1. Check the troubleshooting section
2. Review application logs
3. Test on multiple devices
4. Contact your development team

Remember to keep your mobile app updated with your web application changes to maintain feature parity and data consistency.
