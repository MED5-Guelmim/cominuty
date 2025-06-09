import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Title, Paragraph } from 'react-native-paper';

const CreateLessonScreen = () => {
  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Title>Create Lesson</Title>
        <Paragraph>Lesson creation interface will be implemented here.</Paragraph>
      </View>
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
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
});

export default CreateLessonScreen;
