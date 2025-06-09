import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Chip,
  ActivityIndicator,
  Appbar,
  FAB
} from 'react-native-paper';
import { useFocusEffect, useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const TeacherDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { user, logout } = useAuth();
  const navigation = useNavigation();

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('/api/dashboard/teacher');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchDashboardData();
    }, [])
  );

  const onRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  const handleLogout = () => {
    logout();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6200ee" />
        <Paragraph style={styles.loadingText}>Loading dashboard...</Paragraph>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Teacher Dashboard" />
        <Appbar.Action icon="logout" onPress={handleLogout} />
      </Appbar.Header>

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <View style={styles.welcomeSection}>
          <Title style={styles.welcomeTitle}>Welcome, {user?.username}!</Title>
          <Paragraph style={styles.subtitle}>Manage your lessons and quizzes</Paragraph>
        </View>

        {dashboardData && (
          <Card style={styles.statsCard}>
            <Card.Content>
              <Title style={styles.cardTitle}>Your Content</Title>
              <View style={styles.statsContainer}>
                <View style={styles.statItem}>
                  <Icon name="book" size={24} color="#6200ee" />
                  <Paragraph style={styles.statNumber}>{dashboardData.stats.total_lessons}</Paragraph>
                  <Paragraph style={styles.statLabel}>Lessons</Paragraph>
                </View>
                <View style={styles.statItem}>
                  <Icon name="quiz" size={24} color="#03dac6" />
                  <Paragraph style={styles.statNumber}>{dashboardData.stats.total_quizzes}</Paragraph>
                  <Paragraph style={styles.statLabel}>Quizzes</Paragraph>
                </View>
                <View style={styles.statItem}>
                  <Icon name="people" size={24} color="#4caf50" />
                  <Paragraph style={styles.statNumber}>{dashboardData.stats.total_attempts}</Paragraph>
                  <Paragraph style={styles.statLabel}>Attempts</Paragraph>
                </View>
              </View>
            </Card.Content>
          </Card>
        )}

        <View style={styles.actionsContainer}>
          <Card style={styles.actionCard}>
            <TouchableOpacity onPress={() => navigation.navigate('CreateLesson')}>
              <Card.Content style={styles.actionContent}>
                <Icon name="add-circle" size={32} color="#6200ee" />
                <Title style={styles.actionTitle}>Create Lesson</Title>
                <Paragraph style={styles.actionDescription}>
                  Upload new learning materials
                </Paragraph>
              </Card.Content>
            </TouchableOpacity>
          </Card>

          <Card style={styles.actionCard}>
            <TouchableOpacity onPress={() => navigation.navigate('CreateQuiz')}>
              <Card.Content style={styles.actionContent}>
                <Icon name="quiz" size={32} color="#03dac6" />
                <Title style={styles.actionTitle}>Create Quiz</Title>
                <Paragraph style={styles.actionDescription}>
                  Design interactive assessments
                </Paragraph>
              </Card.Content>
            </TouchableOpacity>
          </Card>
        </View>

        <View style={styles.bottomSpacing} />
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    color: '#666',
  },
  scrollView: {
    flex: 1,
  },
  welcomeSection: {
    padding: 20,
    backgroundColor: '#6200ee',
  },
  welcomeTitle: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
  },
  subtitle: {
    color: 'rgba(255, 255, 255, 0.8)',
    marginTop: 4,
  },
  statsCard: {
    margin: 16,
    elevation: 4,
  },
  cardTitle: {
    textAlign: 'center',
    marginBottom: 16,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
  },
  actionsContainer: {
    padding: 16,
    gap: 16,
  },
  actionCard: {
    elevation: 2,
  },
  actionContent: {
    alignItems: 'center',
    padding: 20,
  },
  actionTitle: {
    marginTop: 12,
    marginBottom: 8,
  },
  actionDescription: {
    textAlign: 'center',
    color: '#666',
  },
  bottomSpacing: {
    height: 20,
  },
});

export default TeacherDashboard;
