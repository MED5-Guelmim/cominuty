import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Title, Paragraph, Appbar } from 'react-native-paper';

const QuizzesScreen = () => {
  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Quizzes" />
      </Appbar.Header>
      <View style={styles.content}>
        <Title>Quizzes Screen</Title>
        <Paragraph>Quiz listing and management will be implemented here.</Paragraph>
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

export default QuizzesScreen;
