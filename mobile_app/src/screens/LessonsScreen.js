import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Chip,
  ActivityIndicator,
  Appbar,
  Searchbar,
  FAB
} from 'react-native-paper';
import { useFocusEffect, useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const LessonsScreen = () => {
  const [lessons, setLessons] = useState([]);
  const [filteredLessons, setFilteredLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const { user } = useAuth();
  const navigation = useNavigation();

  const fetchLessons = async () => {
    try {
      const response = await axios.get('/api/lessons');
      setLessons(response.data.lessons);
      setFilteredLessons(response.data.lessons);
    } catch (error) {
      console.error('Error fetching lessons:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchLessons();
    }, [])
  );

  const onRefresh = () => {
    setRefreshing(true);
    fetchLessons();
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    if (query.trim() === '') {
      setFilteredLessons(lessons);
    } else {
      const filtered = lessons.filter(lesson =>
        lesson.title.toLowerCase().includes(query.toLowerCase()) ||
        lesson.teacher.toLowerCase().includes(query.toLowerCase())
      );
      setFilteredLessons(filtered);
    }
  };

  const getFileTypeIcon = (fileType) => {
    switch (fileType?.toLowerCase()) {
      case 'pdf':
        return 'picture-as-pdf';
      case 'ppt':
      case 'pptx':
        return 'slideshow';
      case 'doc':
      case 'docx':
        return 'description';
      case 'jpg':
      case 'jpeg':
      case 'png':
        return 'image';
      case 'mp4':
      case 'webm':
      case 'ogg':
        return 'play-circle-filled';
      default:
        return 'insert-drive-file';
    }
  };

  const getFileTypeColor = (fileType) => {
    switch (fileType?.toLowerCase()) {
      case 'pdf':
        return '#f44336';
      case 'ppt':
      case 'pptx':
        return '#ff9800';
      case 'doc':
      case 'docx':
        return '#2196f3';
      case 'jpg':
      case 'jpeg':
      case 'png':
        return '#4caf50';
      case 'mp4':
      case 'webm':
      case 'ogg':
        return '#9c27b0';
      default:
        return '#666';
    }
  };

  const renderLessonItem = ({ item }) => (
    <TouchableOpacity
      onPress={() => navigation.navigate('LessonDetail', { lessonId: item.id })}
    >
      <Card style={styles.lessonCard}>
        <Card.Content>
          <View style={styles.lessonHeader}>
            <View style={styles.lessonInfo}>
              <Title style={styles.lessonTitle}>{item.title}</Title>
              <Paragraph style={styles.lessonMeta}>
                by {item.teacher} • {item.section}
              </Paragraph>
              <Paragraph style={styles.lessonDate}>
                {new Date(item.created_at).toLocaleDateString()}
              </Paragraph>
            </View>
            <View style={styles.lessonIcon}>
              <Icon
                name={getFileTypeIcon(item.file_type)}
                size={32}
                color={getFileTypeColor(item.file_type)}
              />
            </View>
          </View>
          
          <View style={styles.lessonFooter}>
            {item.file_type && (
              <Chip
                mode="outlined"
                style={styles.fileTypeChip}
                textStyle={styles.chipText}
              >
                {item.file_type.toUpperCase()}
              </Chip>
            )}
            {user?.role === 'teacher' && (
              <Chip
                mode="outlined"
                style={[
                  styles.statusChip,
                  { backgroundColor: item.is_published ? '#e8f5e8' : '#ffeaea' }
                ]}
                textStyle={[
                  styles.chipText,
                  { color: item.is_published ? '#4caf50' : '#f44336' }
                ]}
              >
                {item.is_published ? 'Published' : 'Draft'}
              </Chip>
            )}
          </View>
        </Card.Content>
      </Card>
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Icon name="book" size={64} color="#ccc" />
      <Title style={styles.emptyTitle}>No lessons found</Title>
      <Paragraph style={styles.emptyText}>
        {searchQuery ? 'Try adjusting your search terms' : 'Check back later for new lessons'}
      </Paragraph>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.container}>
        <Appbar.Header>
          <Appbar.Content title="Lessons" />
        </Appbar.Header>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#6200ee" />
          <Paragraph style={styles.loadingText}>Loading lessons...</Paragraph>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Lessons" />
      </Appbar.Header>

      <View style={styles.content}>
        <Searchbar
          placeholder="Search lessons..."
          onChangeText={handleSearch}
          value={searchQuery}
          style={styles.searchBar}
        />

        <FlatList
          data={filteredLessons}
          renderItem={renderLessonItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.listContainer}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          ListEmptyComponent={renderEmptyState}
          showsVerticalScrollIndicator={false}
        />
      </View>

      {user?.role === 'teacher' && (
        <FAB
          style={styles.fab}
          icon="plus"
          onPress={() => navigation.navigate('CreateLesson')}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
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
  searchBar: {
    margin: 16,
    elevation: 2,
  },
  listContainer: {
    paddingHorizontal: 16,
    paddingBottom: 80,
  },
  lessonCard: {
    marginBottom: 12,
    elevation: 2,
  },
  lessonHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  lessonInfo: {
    flex: 1,
    marginRight: 16,
  },
  lessonTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  lessonMeta: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  lessonDate: {
    fontSize: 12,
    color: '#999',
  },
  lessonIcon: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  lessonFooter: {
    flexDirection: 'row',
    marginTop: 12,
    gap: 8,
  },
  fileTypeChip: {
    height: 28,
  },
  statusChip: {
    height: 28,
    borderWidth: 0,
  },
  chipText: {
    fontSize: 10,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  emptyTitle: {
    marginTop: 16,
    color: '#666',
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    marginTop: 8,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#6200ee',
  },
});

export default LessonsScreen;
