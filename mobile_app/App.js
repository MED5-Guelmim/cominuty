import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';
import Icon from 'react-native-vector-icons/MaterialIcons';
import * as SecureStore from 'expo-secure-store';

// Import screens
import LoginScreen from './src/screens/LoginScreen';
import StudentDashboard from './src/screens/StudentDashboard';
import TeacherDashboard from './src/screens/TeacherDashboard';
import AdminDashboard from './src/screens/AdminDashboard';
import LessonsScreen from './src/screens/LessonsScreen';
import LessonDetailScreen from './src/screens/LessonDetailScreen';
import QuizzesScreen from './src/screens/QuizzesScreen';
import TakeQuizScreen from './src/screens/TakeQuizScreen';
import CreateLessonScreen from './src/screens/CreateLessonScreen';
import CreateQuizScreen from './src/screens/CreateQuizScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import AnalyticsScreen from './src/screens/AnalyticsScreen';

// Import context
import { AuthProvider, useAuth } from './src/context/AuthContext';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Student Tab Navigator
function StudentTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          if (route.name === 'Dashboard') {
            iconName = 'dashboard';
          } else if (route.name === 'Lessons') {
            iconName = 'book';
          } else if (route.name === 'Quizzes') {
            iconName = 'quiz';
          } else if (route.name === 'Profile') {
            iconName = 'person';
          }
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#6200ee',
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}
    >
      <Tab.Screen name="Dashboard" component={StudentDashboard} />
      <Tab.Screen name="Lessons" component={LessonsScreen} />
      <Tab.Screen name="Quizzes" component={QuizzesScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

// Teacher Tab Navigator
function TeacherTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          if (route.name === 'Dashboard') {
            iconName = 'dashboard';
          } else if (route.name === 'Lessons') {
            iconName = 'book';
          } else if (route.name === 'Quizzes') {
            iconName = 'quiz';
          } else if (route.name === 'Analytics') {
            iconName = 'analytics';
          } else if (route.name === 'Profile') {
            iconName = 'person';
          }
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#6200ee',
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}
    >
      <Tab.Screen name="Dashboard" component={TeacherDashboard} />
      <Tab.Screen name="Lessons" component={LessonsScreen} />
      <Tab.Screen name="Quizzes" component={QuizzesScreen} />
      <Tab.Screen name="Analytics" component={AnalyticsScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

// Admin Tab Navigator
function AdminTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          if (route.name === 'Dashboard') {
            iconName = 'dashboard';
          } else if (route.name === 'Analytics') {
            iconName = 'analytics';
          } else if (route.name === 'Profile') {
            iconName = 'person';
          }
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#6200ee',
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}
    >
      <Tab.Screen name="Dashboard" component={AdminDashboard} />
      <Tab.Screen name="Analytics" component={AnalyticsScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

// Main App Navigator
function AppNavigator() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return null; // You can add a loading screen here
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {user ? (
          <>
            {user.role === 'student' && (
              <Stack.Screen name="StudentMain" component={StudentTabs} />
            )}
            {user.role === 'teacher' && (
              <Stack.Screen name="TeacherMain" component={TeacherTabs} />
            )}
            {user.role === 'admin' && (
              <Stack.Screen name="AdminMain" component={AdminTabs} />
            )}
            <Stack.Screen 
              name="LessonDetail" 
              component={LessonDetailScreen}
              options={{ headerShown: true, title: 'Lesson' }}
            />
            <Stack.Screen 
              name="TakeQuiz" 
              component={TakeQuizScreen}
              options={{ headerShown: true, title: 'Quiz' }}
            />
            <Stack.Screen 
              name="CreateLesson" 
              component={CreateLessonScreen}
              options={{ headerShown: true, title: 'Create Lesson' }}
            />
            <Stack.Screen 
              name="CreateQuiz" 
              component={CreateQuizScreen}
              options={{ headerShown: true, title: 'Create Quiz' }}
            />
          </>
        ) : (
          <Stack.Screen name="Login" component={LoginScreen} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <PaperProvider>
      <AuthProvider>
        <StatusBar style="auto" />
        <AppNavigator />
      </AuthProvider>
    </PaperProvider>
  );
}
