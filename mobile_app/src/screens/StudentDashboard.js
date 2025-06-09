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
  Surface,
  Divider
} from 'react-native-paper';
import { useFocusEffect, useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const StudentDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { user, logout } = useAuth();
  const navigation = useNavigation();

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('/api/dashboard/student');
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

  const renderStatsCard = () => {
    if (!dashboardData) return null;

    const { stats } = dashboardData;
    return (
      <Card style={styles.statsCard}>
        <Card.Content>
          <Title style={styles.cardTitle}>Your Progress</Title>
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Icon name="book" size={24} color="#6200ee" />
              <Paragraph style={styles.statNumber}>{stats.total_lessons}</Paragraph>
              <Paragraph style={styles.statLabel}>Lessons</Paragraph>
            </View>
            <View style={styles.statItem}>
              <Icon name="quiz" size={24} color="#03dac6" />
              <Paragraph style={styles.statNumber}>{stats.total_quizzes}</Paragraph>
              <Paragraph style={styles.statLabel}>Quizzes</Paragraph>
            </View>
            <View style={styles.statItem}>
              <Icon name="check-circle" size={24} color="#4caf50" />
              <Paragraph style={styles.statNumber}>{stats.completed_quizzes}</Paragraph>
              <Paragraph style={styles.statLabel}>Completed</Paragraph>
            </View>
          </View>
        </Card.Content>
      </Card>
    );
  };

  const renderRecentLessons = () => {
    if (!dashboardData?.lessons?.length) return null;

    return (
      <Card style={styles.sectionCard}>
        <Card.Content>
          <View style={styles.sectionHeader}>
            <Title style={styles.sectionTitle}>Recent Lessons</Title>
            <Button
              mode="text"
              onPress={() => navigation.navigate('Lessons')}
              compact
            >
              View All
            </Button>
          </View>
          {dashboardData.lessons.slice(0, 3).map((lesson) => (
            <TouchableOpacity
              key={lesson.id}
              style={styles.listItem}
              onPress={() => navigation.navigate('LessonDetail', { lessonId: lesson.id })}
            >
              <View style={styles.listItemContent}>
                <View style={styles.listItemIcon}>
                  <Icon name="book" size={20} color="#6200ee" />
                </View>
                <View style={styles.listItemText}>
                  <Paragraph style={styles.listItemTitle}>{lesson.title}</Paragraph>
                  <Paragraph style={styles.listItemSubtitle}>
                    by {lesson.teacher} • {new Date(lesson.created_at).toLocaleDateString()}
                  </Paragraph>
                </View>
                <Icon name="chevron-right" size={20} color="#666" />
              </View>
            </TouchableOpacity>
          ))}
        </Card.Content>
      </Card>
    );
  };

  const renderRecentQuizzes = () => {
    if (!dashboardData?.quizzes?.length) return null;

    return (
      <Card style={styles.sectionCard}>
        <Card.Content>
          <View style={styles.sectionHeader}>
            <Title style={styles.sectionTitle}>Available Quizzes</Title>
            <Button
              mode="text"
              onPress={() => navigation.navigate('Quizzes')}
              compact
            >
              View All
            </Button>
          </View>
          {dashboardData.quizzes.slice(0, 3).map((quiz) => (
            <TouchableOpacity
              key={quiz.id}
              style={styles.listItem}
              onPress={() => navigation.navigate('TakeQuiz', { quizId: quiz.id })}
            >
              <View style={styles.listItemContent}>
                <View style={styles.listItemIcon}>
                  <Icon name="quiz" size={20} color="#03dac6" />
                </View>
                <View style={styles.listItemText}>
                  <Paragraph style={styles.listItemTitle}>{quiz.title}</Paragraph>
                  <Paragraph style={styles.listItemSubtitle}>
                    by {quiz.teacher} • {new Date(quiz.created_at).toLocaleDateString()}
                  </Paragraph>
                  {quiz.attempted && (
                    <Chip
                      mode="outlined"
                      style={styles.completedChip}
                      textStyle={styles.chipText}
                    >
                      Completed: {quiz.score}
                    </Chip>
                  )}
                </View>
                <Icon name="chevron-right" size={20} color="#666" />
              </View>
            </TouchableOpacity>
          ))}
        </Card.Content>
      </Card>
    );
  };

  const renderRecentAttempts = () => {
    if (!dashboardData?.recent_attempts?.length) return null;

    return (
      <Card style={styles.sectionCard}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Recent Quiz Results</Title>
          {dashboardData.recent_attempts.map((attempt, index) => (
            <View key={index} style={styles.attemptItem}>
              <View style={styles.attemptContent}>
                <Paragraph style={styles.attemptTitle}>{attempt.quiz_title}</Paragraph>
                <Paragraph style={styles.attemptDate}>
                  {new Date(attempt.completed_at).toLocaleDateString()}
                </Paragraph>
              </View>
              <View style={styles.attemptScore}>
                <Chip
                  mode="outlined"
                  style={[
                    styles.scoreChip,
                    { backgroundColor: attempt.percentage >= 70 ? '#e8f5e8' : '#ffeaea' }
                  ]}
                  textStyle={[
                    styles.chipText,
                    { color: attempt.percentage >= 70 ? '#4caf50' : '#f44336' }
                  ]}
                >
                  {attempt.percentage}%
                </Chip>
              </View>
            </View>
          ))}
        </Card.Content>
      </Card>
    );
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
        <Appbar.Content title="Dashboard" />
        <Appbar.Action icon="logout" onPress={handleLogout} />
      </Appbar.Header>

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <View style={styles.welcomeSection}>
          <Title style={styles.welcomeTitle}>Welcome back, {user?.username}!</Title>
          {user?.section && (
            <Paragraph style={styles.sectionInfo}>
              Section: {user.section.name}
            </Paragraph>
          )}
        </View>

        {renderStatsCard()}
        {renderRecentLessons()}
        {renderRecentQuizzes()}
        {renderRecentAttempts()}

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
  sectionInfo: {
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
  sectionCard: {
    margin: 16,
    marginTop: 0,
    elevation: 2,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
  },
  listItem: {
    marginBottom: 12,
  },
  listItemContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
  },
  listItemIcon: {
    marginRight: 12,
  },
  listItemText: {
    flex: 1,
  },
  listItemTitle: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  listItemSubtitle: {
    fontSize: 12,
    color: '#666',
  },
  completedChip: {
    marginTop: 8,
    alignSelf: 'flex-start',
  },
  chipText: {
    fontSize: 10,
  },
  attemptItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  attemptContent: {
    flex: 1,
  },
  attemptTitle: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  attemptDate: {
    fontSize: 12,
    color: '#666',
  },
  attemptScore: {
    marginLeft: 12,
  },
  scoreChip: {
    borderWidth: 0,
  },
  bottomSpacing: {
    height: 20,
  },
});

export default StudentDashboard;
