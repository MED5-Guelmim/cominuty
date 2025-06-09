import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  RefreshControl
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  ActivityIndicator,
  Appbar
} from 'react-native-paper';
import { useFocusEffect } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { user, logout } = useAuth();

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('/api/dashboard/admin');
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
        <Appbar.Content title="Admin Dashboard" />
        <Appbar.Action icon="logout" onPress={handleLogout} />
      </Appbar.Header>

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <View style={styles.welcomeSection}>
          <Title style={styles.welcomeTitle}>Admin Panel</Title>
          <Paragraph style={styles.subtitle}>Platform Overview</Paragraph>
        </View>

        {dashboardData && (
          <Card style={styles.statsCard}>
            <Card.Content>
              <Title style={styles.cardTitle}>Platform Statistics</Title>
              <View style={styles.statsGrid}>
                <View style={styles.statItem}>
                  <Icon name="people" size={24} color="#6200ee" />
                  <Paragraph style={styles.statNumber}>{dashboardData.stats.total_users}</Paragraph>
                  <Paragraph style={styles.statLabel}>Total Users</Paragraph>
                </View>
                <View style={styles.statItem}>
                  <Icon name="school" size={24} color="#03dac6" />
                  <Paragraph style={styles.statNumber}>{dashboardData.stats.total_teachers}</Paragraph>
                  <Paragraph style={styles.statLabel}>Teachers</Paragraph>
                </View>
                <View style={styles.statItem}>
                  <Icon name="person" size={24} color="#4caf50" />
                  <Paragraph style={styles.statNumber}>{dashboardData.stats.total_students}</Paragraph>
                  <Paragraph style={styles.statLabel}>Students</Paragraph>
                </View>
                <View style={styles.statItem}>
                  <Icon name="book" size={24} color="#ff9800" />
                  <Paragraph style={styles.statNumber}>{dashboardData.stats.total_lessons}</Paragraph>
                  <Paragraph style={styles.statLabel}>Lessons</Paragraph>
                </View>
                <View style={styles.statItem}>
                  <Icon name="quiz" size={24} color="#9c27b0" />
                  <Paragraph style={styles.statNumber}>{dashboardData.stats.total_quizzes}</Paragraph>
                  <Paragraph style={styles.statLabel}>Quizzes</Paragraph>
                </View>
                <View style={styles.statItem}>
                  <Icon name="class" size={24} color="#f44336" />
                  <Paragraph style={styles.statNumber}>{dashboardData.stats.total_sections}</Paragraph>
                  <Paragraph style={styles.statLabel}>Sections</Paragraph>
                </View>
              </View>
            </Card.Content>
          </Card>
        )}

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
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
    width: '30%',
    marginBottom: 20,
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 10,
    color: '#666',
    textAlign: 'center',
  },
  bottomSpacing: {
    height: 20,
  },
});

export default AdminDashboard;
