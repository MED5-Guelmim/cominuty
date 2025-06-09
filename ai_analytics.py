"""
AI Analytics Module for School Platform
Provides intelligent insights and analysis of student performance and learning patterns
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import json
from collections import defaultdict

class StudentAnalytics:
    """
    AI-powered analytics for student performance tracking and insights
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.performance_model = LinearRegression()
        self.clustering_model = KMeans(n_clusters=3, random_state=42)
        
    def analyze_student_performance(self, student_interactions, quiz_attempts):
        """
        Analyze individual student performance and learning patterns
        
        Args:
            student_interactions: List of StudentInteraction objects
            quiz_attempts: List of QuizAttempt objects
            
        Returns:
            dict: Comprehensive analysis results
        """
        if not student_interactions and not quiz_attempts:
            return self._empty_analysis()
            
        # Convert to DataFrames for analysis
        interactions_df = self._interactions_to_dataframe(student_interactions)
        attempts_df = self._attempts_to_dataframe(quiz_attempts)
        
        analysis = {
            'performance_metrics': self._calculate_performance_metrics(attempts_df),
            'learning_patterns': self._analyze_learning_patterns(interactions_df),
            'engagement_score': self._calculate_engagement_score(interactions_df),
            'difficulty_areas': self._identify_difficulty_areas(attempts_df),
            'progress_trend': self._calculate_progress_trend(attempts_df),
            'recommendations': self._generate_recommendations(interactions_df, attempts_df),
            'predicted_performance': self._predict_future_performance(attempts_df)
        }
        
        return analysis
    
    def analyze_class_performance(self, all_students_data):
        """
        Analyze overall class performance and identify patterns
        
        Args:
            all_students_data: Dict of student_id -> (interactions, attempts)
            
        Returns:
            dict: Class-wide analysis results
        """
        if not all_students_data:
            return self._empty_class_analysis()
            
        class_metrics = []
        student_profiles = []
        
        for student_id, (interactions, attempts) in all_students_data.items():
            student_analysis = self.analyze_student_performance(interactions, attempts)
            
            # Extract key metrics for class analysis
            metrics = {
                'student_id': student_id,
                'avg_score': student_analysis['performance_metrics']['average_score'],
                'engagement': student_analysis['engagement_score'],
                'progress_rate': student_analysis['progress_trend']['slope'],
                'quiz_count': len(attempts) if attempts else 0,
                'lesson_views': len([i for i in interactions if i.interaction_type == 'lesson_view']) if interactions else 0
            }
            class_metrics.append(metrics)
            student_profiles.append(student_analysis)
        
        # Convert to DataFrame for analysis
        class_df = pd.DataFrame(class_metrics)
        
        if class_df.empty:
            return self._empty_class_analysis()
        
        # Perform clustering to identify student groups
        feature_columns = ['avg_score', 'engagement', 'progress_rate', 'quiz_count', 'lesson_views']
        features = class_df[feature_columns].fillna(0)
        
        if len(features) >= 3:  # Need at least 3 students for clustering
            scaled_features = self.scaler.fit_transform(features)
            clusters = self.clustering_model.fit_predict(scaled_features)
            class_df['cluster'] = clusters
        else:
            class_df['cluster'] = 0
        
        analysis = {
            'class_overview': self._calculate_class_overview(class_df),
            'performance_distribution': self._analyze_performance_distribution(class_df),
            'student_groups': self._analyze_student_groups(class_df),
            'at_risk_students': self._identify_at_risk_students(class_df),
            'top_performers': self._identify_top_performers(class_df),
            'engagement_insights': self._analyze_class_engagement(class_df),
            'recommendations': self._generate_class_recommendations(class_df)
        }
        
        return analysis
    
    def _interactions_to_dataframe(self, interactions):
        """Convert StudentInteraction objects to DataFrame"""
        if not interactions:
            return pd.DataFrame()
            
        data = []
        for interaction in interactions:
            data.append({
                'timestamp': interaction.timestamp,
                'interaction_type': interaction.interaction_type,
                'content_id': interaction.content_id,
                'duration': interaction.duration or 0,
                'performance_score': interaction.performance_score or 0
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    def _attempts_to_dataframe(self, attempts):
        """Convert QuizAttempt objects to DataFrame"""
        if not attempts:
            return pd.DataFrame()
            
        data = []
        for attempt in attempts:
            score_percentage = (attempt.score / attempt.total_points * 100) if attempt.total_points > 0 else 0
            data.append({
                'completed_at': attempt.completed_at,
                'score': attempt.score,
                'total_points': attempt.total_points,
                'score_percentage': score_percentage,
                'quiz_id': attempt.quiz_id
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df['completed_at'] = pd.to_datetime(df['completed_at'])
            df = df.sort_values('completed_at')
        return df
    
    def _calculate_performance_metrics(self, attempts_df):
        """Calculate basic performance metrics"""
        if attempts_df.empty:
            return {
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0,
                'total_attempts': 0,
                'improvement_rate': 0
            }
        
        metrics = {
            'average_score': float(attempts_df['score_percentage'].mean()),
            'highest_score': float(attempts_df['score_percentage'].max()),
            'lowest_score': float(attempts_df['score_percentage'].min()),
            'total_attempts': int(len(attempts_df)),
            'improvement_rate': float(self._calculate_improvement_rate(attempts_df))
        }
        
        return metrics
    
    def _analyze_learning_patterns(self, interactions_df):
        """Analyze learning patterns from interactions"""
        if interactions_df.empty:
            return {
                'preferred_time': 'No data',
                'session_duration': 0,
                'content_preference': 'No data',
                'learning_consistency': 0
            }
        
        # Analyze time patterns
        interactions_df['hour'] = interactions_df['timestamp'].dt.hour
        preferred_hour = interactions_df['hour'].mode().iloc[0] if not interactions_df['hour'].mode().empty else 12
        
        # Convert hour to readable time
        if 6 <= preferred_hour < 12:
            preferred_time = 'Morning'
        elif 12 <= preferred_hour < 18:
            preferred_time = 'Afternoon'
        elif 18 <= preferred_hour < 22:
            preferred_time = 'Evening'
        else:
            preferred_time = 'Night'
        
        # Calculate average session duration
        avg_duration = interactions_df['duration'].mean()
        
        # Analyze content preference
        content_counts = interactions_df['interaction_type'].value_counts()
        content_preference = content_counts.index[0] if not content_counts.empty else 'No data'
        
        # Calculate learning consistency (days with activity)
        unique_days = interactions_df['timestamp'].dt.date.nunique()
        total_days = (interactions_df['timestamp'].max() - interactions_df['timestamp'].min()).days + 1
        consistency = (unique_days / total_days) * 100 if total_days > 0 else 0
        
        return {
            'preferred_time': preferred_time,
            'session_duration': float(avg_duration),
            'content_preference': content_preference,
            'learning_consistency': float(consistency)
        }
    
    def _calculate_engagement_score(self, interactions_df):
        """Calculate student engagement score (0-100)"""
        if interactions_df.empty:
            return 0
        
        # Factors for engagement calculation
        factors = {
            'frequency': min(len(interactions_df) / 10, 1) * 30,  # Max 30 points for frequency
            'duration': min(interactions_df['duration'].mean() / 300, 1) * 25,  # Max 25 points for duration
            'consistency': self._calculate_consistency_score(interactions_df) * 25,  # Max 25 points
            'variety': self._calculate_variety_score(interactions_df) * 20  # Max 20 points
        }
        
        engagement_score = sum(factors.values())
        return float(min(engagement_score, 100))
    
    def _calculate_consistency_score(self, interactions_df):
        """Calculate consistency score based on regular activity"""
        if interactions_df.empty:
            return 0
        
        # Group by date and count interactions per day
        daily_activity = interactions_df.groupby(interactions_df['timestamp'].dt.date).size()
        
        # Calculate coefficient of variation (lower is more consistent)
        if len(daily_activity) > 1:
            cv = daily_activity.std() / daily_activity.mean()
            consistency = max(0, 1 - cv)  # Invert so higher is better
        else:
            consistency = 1 if len(daily_activity) == 1 else 0
        
        return consistency
    
    def _calculate_variety_score(self, interactions_df):
        """Calculate variety score based on different types of interactions"""
        if interactions_df.empty:
            return 0
        
        unique_types = interactions_df['interaction_type'].nunique()
        max_types = 3  # lesson_view, quiz_attempt, puzzle_solve
        
        return min(unique_types / max_types, 1)
    
    def _identify_difficulty_areas(self, attempts_df):
        """Identify areas where student is struggling"""
        if attempts_df.empty:
            return []
        
        # Group by quiz and calculate average performance
        quiz_performance = attempts_df.groupby('quiz_id')['score_percentage'].mean()
        
        # Identify quizzes with below-average performance
        overall_avg = attempts_df['score_percentage'].mean()
        difficulty_areas = []
        
        for quiz_id, avg_score in quiz_performance.items():
            if avg_score < overall_avg * 0.8:  # 20% below average
                difficulty_areas.append({
                    'quiz_id': int(quiz_id),
                    'average_score': float(avg_score),
                    'attempts': int(len(attempts_df[attempts_df['quiz_id'] == quiz_id]))
                })
        
        return difficulty_areas
    
    def _calculate_progress_trend(self, attempts_df):
        """Calculate progress trend over time"""
        if len(attempts_df) < 2:
            return {'trend': 'insufficient_data', 'slope': 0, 'r_squared': 0}
        
        # Prepare data for linear regression
        attempts_df = attempts_df.sort_values('completed_at')
        X = np.arange(len(attempts_df)).reshape(-1, 1)
        y = attempts_df['score_percentage'].values
        
        # Fit linear regression
        self.performance_model.fit(X, y)
        slope = self.performance_model.coef_[0]
        r_squared = self.performance_model.score(X, y)
        
        # Determine trend
        if slope > 2:
            trend = 'improving'
        elif slope < -2:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'slope': float(slope),
            'r_squared': float(r_squared)
        }
    
    def _generate_recommendations(self, interactions_df, attempts_df):
        """Generate personalized recommendations"""
        recommendations = []
        
        # Performance-based recommendations
        if not attempts_df.empty:
            avg_score = attempts_df['score_percentage'].mean()
            
            if avg_score < 60:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'high',
                    'message': 'Consider reviewing lesson materials before taking quizzes',
                    'message_ar': 'فكر في مراجعة مواد الدرس قبل أداء الاختبارات',
                    'message_fr': 'Considérez réviser les matériaux de cours avant de passer les quiz',
                    'action': 'review_lessons'
                })
            elif avg_score > 85:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'low',
                    'message': 'Excellent performance! Try more challenging content',
                    'message_ar': 'أداء ممتاز! جرب محتوى أكثر تحدياً',
                    'message_fr': 'Performance excellente! Essayez du contenu plus difficile',
                    'action': 'advanced_content'
                })
        
        # Engagement-based recommendations
        if not interactions_df.empty:
            engagement = self._calculate_engagement_score(interactions_df)
            
            if engagement < 40:
                recommendations.append({
                    'type': 'engagement',
                    'priority': 'medium',
                    'message': 'Try to engage more regularly with the platform',
                    'message_ar': 'حاول التفاعل بانتظام أكثر مع المنصة',
                    'message_fr': 'Essayez de vous engager plus régulièrement avec la plateforme',
                    'action': 'increase_activity'
                })
        
        # Learning pattern recommendations
        patterns = self._analyze_learning_patterns(interactions_df)
        if patterns['learning_consistency'] < 50:
            recommendations.append({
                'type': 'consistency',
                'priority': 'medium',
                'message': 'Try to maintain a more consistent study schedule',
                'message_ar': 'حاول الحفاظ على جدول دراسي أكثر انتظاماً',
                'message_fr': 'Essayez de maintenir un horaire d\'étude plus cohérent',
                'action': 'schedule_study'
            })
        
        return recommendations
    
    def _predict_future_performance(self, attempts_df):
        """Predict future performance based on current trends"""
        if len(attempts_df) < 3:
            return {'prediction': 'insufficient_data', 'confidence': 0}
        
        trend = self._calculate_progress_trend(attempts_df)
        current_avg = attempts_df['score_percentage'].tail(3).mean()
        
        # Simple prediction based on trend
        predicted_score = current_avg + (trend['slope'] * 2)  # Predict 2 attempts ahead
        predicted_score = max(0, min(100, predicted_score))  # Clamp to valid range
        
        confidence = min(trend['r_squared'] * 100, 95)  # Max 95% confidence
        
        return {
            'prediction': float(predicted_score),
            'confidence': float(confidence),
            'trend': trend['trend']
        }
    
    def _calculate_class_overview(self, class_df):
        """Calculate overall class statistics"""
        return {
            'total_students': int(len(class_df)),
            'average_score': float(class_df['avg_score'].mean()),
            'average_engagement': float(class_df['engagement'].mean()),
            'total_quiz_attempts': int(class_df['quiz_count'].sum()),
            'total_lesson_views': int(class_df['lesson_views'].sum())
        }
    
    def _analyze_performance_distribution(self, class_df):
        """Analyze how performance is distributed across the class"""
        if class_df.empty:
            return {}
        
        scores = class_df['avg_score']
        
        return {
            'excellent': int(len(scores[scores >= 90])),  # 90-100%
            'good': int(len(scores[(scores >= 80) & (scores < 90)])),  # 80-89%
            'satisfactory': int(len(scores[(scores >= 70) & (scores < 80)])),  # 70-79%
            'needs_improvement': int(len(scores[scores < 70]))  # Below 70%
        }
    
    def _analyze_student_groups(self, class_df):
        """Analyze student groups based on clustering"""
        if 'cluster' not in class_df.columns:
            return {}
        
        groups = {}
        for cluster_id in class_df['cluster'].unique():
            cluster_data = class_df[class_df['cluster'] == cluster_id]
            
            groups[f'group_{cluster_id}'] = {
                'size': int(len(cluster_data)),
                'avg_score': float(cluster_data['avg_score'].mean()),
                'avg_engagement': float(cluster_data['engagement'].mean()),
                'characteristics': self._describe_cluster(cluster_data)
            }
        
        return groups
    
    def _describe_cluster(self, cluster_data):
        """Describe characteristics of a student cluster"""
        avg_score = cluster_data['avg_score'].mean()
        avg_engagement = cluster_data['engagement'].mean()
        
        if avg_score >= 80 and avg_engagement >= 70:
            return 'High performers with strong engagement'
        elif avg_score >= 70 and avg_engagement < 50:
            return 'Good performers but low engagement'
        elif avg_score < 60:
            return 'Students needing additional support'
        else:
            return 'Average performers'
    
    def _identify_at_risk_students(self, class_df):
        """Identify students who may need additional support"""
        at_risk = class_df[
            (class_df['avg_score'] < 60) | 
            (class_df['engagement'] < 30) |
            (class_df['progress_rate'] < -2)
        ]
        
        return at_risk[['student_id', 'avg_score', 'engagement']].to_dict('records')
    
    def _identify_top_performers(self, class_df):
        """Identify top performing students"""
        top_performers = class_df[
            (class_df['avg_score'] >= 85) & 
            (class_df['engagement'] >= 70)
        ].nlargest(5, 'avg_score')
        
        return top_performers[['student_id', 'avg_score', 'engagement']].to_dict('records')
    
    def _analyze_class_engagement(self, class_df):
        """Analyze overall class engagement patterns"""
        return {
            'highly_engaged': int(len(class_df[class_df['engagement'] >= 70])),
            'moderately_engaged': int(len(class_df[(class_df['engagement'] >= 40) & (class_df['engagement'] < 70)])),
            'low_engagement': int(len(class_df[class_df['engagement'] < 40])),
            'average_engagement': float(class_df['engagement'].mean())
        }
    
    def _generate_class_recommendations(self, class_df):
        """Generate recommendations for the entire class"""
        recommendations = []
        
        avg_score = class_df['avg_score'].mean()
        avg_engagement = class_df['engagement'].mean()
        
        if avg_score < 70:
            recommendations.append({
                'type': 'class_performance',
                'priority': 'high',
                'message': 'Class average is below target. Consider reviewing teaching methods or content difficulty.',
                'message_ar': 'متوسط الفصل أقل من المستهدف. فكر في مراجعة طرق التدريس أو صعوبة المحتوى.',
                'message_fr': 'La moyenne de la classe est en dessous de l\'objectif. Considérez réviser les méthodes d\'enseignement ou la difficulté du contenu.',
                'action': 'review_curriculum'
            })
        
        if avg_engagement < 50:
            recommendations.append({
                'type': 'class_engagement',
                'priority': 'high',
                'message': 'Low class engagement. Consider adding more interactive content.',
                'message_ar': 'مشاركة منخفضة في الفصل. فكر في إضافة محتوى تفاعلي أكثر.',
                'message_fr': 'Faible engagement de la classe. Considérez ajouter plus de contenu interactif.',
                'action': 'increase_interactivity'
            })
        
        at_risk_count = len(self._identify_at_risk_students(class_df))
        if at_risk_count > len(class_df) * 0.2:  # More than 20% at risk
            recommendations.append({
                'type': 'at_risk',
                'priority': 'high',
                'message': f'{at_risk_count} students need additional support.',
                'message_ar': f'{at_risk_count} طلاب يحتاجون دعماً إضافياً.',
                'message_fr': f'{at_risk_count} étudiants ont besoin de soutien supplémentaire.',
                'action': 'provide_support'
            })
        
        return recommendations
    
    def _calculate_improvement_rate(self, attempts_df):
        """Calculate rate of improvement over time"""
        if len(attempts_df) < 2:
            return 0
        
        first_half = attempts_df.head(len(attempts_df) // 2)
        second_half = attempts_df.tail(len(attempts_df) // 2)
        
        first_avg = first_half['score_percentage'].mean()
        second_avg = second_half['score_percentage'].mean()
        
        return second_avg - first_avg
    
    def _empty_analysis(self):
        """Return empty analysis structure"""
        return {
            'performance_metrics': {
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0,
                'total_attempts': 0,
                'improvement_rate': 0
            },
            'learning_patterns': {
                'preferred_time': 'No data',
                'session_duration': 0,
                'content_preference': 'No data',
                'learning_consistency': 0
            },
            'engagement_score': 0,
            'difficulty_areas': [],
            'progress_trend': {'trend': 'no_data', 'slope': 0, 'r_squared': 0},
            'recommendations': [],
            'predicted_performance': {'prediction': 'insufficient_data', 'confidence': 0}
        }
    
    def _empty_class_analysis(self):
        """Return empty class analysis structure"""
        return {
            'class_overview': {
                'total_students': 0,
                'average_score': 0,
                'average_engagement': 0,
                'total_quiz_attempts': 0,
                'total_lesson_views': 0
            },
            'performance_distribution': {
                'excellent': 0,
                'good': 0,
                'satisfactory': 0,
                'needs_improvement': 0
            },
            'student_groups': {},
            'at_risk_students': [],
            'top_performers': [],
            'engagement_insights': {
                'highly_engaged': 0,
                'moderately_engaged': 0,
                'low_engagement': 0,
                'average_engagement': 0
            },
            'recommendations': []
        }

# Utility function to get analytics instance
def get_analytics_instance():
    """Get a singleton instance of StudentAnalytics"""
    if not hasattr(get_analytics_instance, '_instance'):
        get_analytics_instance._instance = StudentAnalytics()
    return get_analytics_instance._instance