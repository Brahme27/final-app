"""
Student History Module
Tracks student learning progress and generates reports
"""

from datetime import datetime
from typing import Dict, List, Any
import json
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class StudentHistory:
    def __init__(self):
        """Initialize student history tracking"""
        self.topics_studied = []
        self.quiz_results = []
        self.quiz_attempts = []  # New property for compatibility with app.py
        self.chat_interactions = []
        self.video_views = []
        self.study_sessions = []
    
    def add_topic_studied(self, class_level: str, subject: str, chapter: str, topic: str):
        """Record that a student has studied a topic"""
        study_record = {
            'timestamp': datetime.now(),
            'class': class_level,
            'subject': subject,
            'chapter': chapter,
            'topic': topic,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S')
        }
        self.topics_studied.append(study_record)
    
    def add_quiz_attempt(self, topic: str, quiz_type: str, score: float, 
                        total_questions: int, correct_answers: int):
        """Record quiz attempt - for compatibility with app.py"""
        quiz_record = {
            'timestamp': datetime.now(),
            'topic': topic,
            'quiz_type': quiz_type,
            'score': score,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S')
        }
        self.quiz_attempts.append(quiz_record)
        
        # Also add to quiz_results for backward compatibility
        self.quiz_results.append(quiz_record)
    
    def add_quiz_result(self, class_level: str, subject: str, topic: str, 
                       score: int, total: int, quiz_type: str = "general"):
        """Record quiz results"""
        quiz_record = {
            'timestamp': datetime.now().isoformat(),
            'class': class_level,
            'subject': subject,
            'topic': topic,
            'score': score,
            'total': total,
            'percentage': (score / total) * 100 if total > 0 else 0,
            'quiz_type': quiz_type,  # 'mini', 'final', 'adaptive'
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S')
        }
        self.quiz_results.append(quiz_record)
    
    def add_chat_interaction(self, topic: str, question: str, response: str):
        """Record chat interactions for learning analytics"""
        chat_record = {
            'timestamp': datetime.now().isoformat(),
            'topic': topic,
            'question': question,
            'response_length': len(response),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S')
        }
        self.chat_interactions.append(chat_record)
    
    def add_video_view(self, topic: str, video_title: str, video_url: str):
        """Record video viewing activity"""
        video_record = {
            'timestamp': datetime.now(),
            'topic': topic,
            'video_title': video_title,
            'video_url': video_url,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S')
        }
        self.video_views.append(video_record)
    
    def add_study_session(self, duration_minutes: int, activities: List[str]):
        """Record study session details"""
        session_record = {
            'timestamp': datetime.now().isoformat(),
            'duration_minutes': duration_minutes,
            'activities': activities,  # ['topic_explanation', 'quiz', 'chat', 'video']
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S')
        }
        self.study_sessions.append(session_record)
    
    def get_topics_by_subject(self, subject: str) -> List[Dict]:
        """Get all topics studied for a specific subject"""
        return [topic for topic in self.topics_studied if topic['subject'] == subject]
    
    def get_quiz_performance_summary(self) -> Dict[str, Any]:
        """Get summary of quiz performance"""
        if not self.quiz_results:
            return {
                'total_quizzes': 0,
                'average_score': 0,
                'best_subject': None,
                'weakest_subject': None,
                'improvement_trend': None
            }
        
        total_quizzes = len(self.quiz_results)
        average_score = sum(quiz['percentage'] for quiz in self.quiz_results) / total_quizzes
        
        # Subject-wise performance
        subject_performance = {}
        for quiz in self.quiz_results:
            subject = quiz['subject']
            if subject not in subject_performance:
                subject_performance[subject] = []
            subject_performance[subject].append(quiz['percentage'])
        
        subject_averages = {
            subject: sum(scores) / len(scores) 
            for subject, scores in subject_performance.items()
        }
        
        best_subject = max(subject_averages.items(), key=lambda x: x[1]) if subject_averages else None
        weakest_subject = min(subject_averages.items(), key=lambda x: x[1]) if subject_averages else None
        
        # Calculate improvement trend (last 5 vs first 5 quizzes)
        improvement_trend = None
        if total_quizzes >= 6:
            first_5_avg = sum(quiz['percentage'] for quiz in self.quiz_results[:5]) / 5
            last_5_avg = sum(quiz['percentage'] for quiz in self.quiz_results[-5:]) / 5
            improvement_trend = last_5_avg - first_5_avg
        
        return {
            'total_quizzes': total_quizzes,
            'average_score': round(average_score, 1),
            'best_subject': best_subject,
            'weakest_subject': weakest_subject,
            'improvement_trend': round(improvement_trend, 1) if improvement_trend else None,
            'subject_performance': subject_averages
        }
    
    def get_learning_streaks(self) -> Dict[str, Any]:
        """Calculate learning streaks and consistency"""
        if not self.topics_studied:
            return {'current_streak': 0, 'longest_streak': 0, 'study_days': 0}
        
        # Get unique study dates
        study_dates = list(set(topic['date'] for topic in self.topics_studied))
        study_dates.sort()
        
        # Calculate current streak
        current_streak = 0
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if studied today or yesterday
        if study_dates and (study_dates[-1] == today or 
                           (len(study_dates) > 1 and study_dates[-1] == datetime.now().strftime('%Y-%m-%d'))):
            current_streak = 1
            
            # Count consecutive days backwards
            for i in range(len(study_dates) - 2, -1, -1):
                date_obj = datetime.strptime(study_dates[i], '%Y-%m-%d')
                next_date_obj = datetime.strptime(study_dates[i + 1], '%Y-%m-%d')
                
                if (next_date_obj - date_obj).days == 1:
                    current_streak += 1
                else:
                    break
        
        return {
            'current_streak': current_streak,
            'longest_streak': current_streak,  # Simplified for now
            'study_days': len(study_dates),
            'total_topics': len(self.topics_studied)
        }
    
    def identify_weak_areas(self) -> List[Dict[str, Any]]:
        """Identify areas where student needs more practice"""
        weak_areas = []
        
        if not self.quiz_results:
            return weak_areas
        
        # Group quiz results by topic
        topic_performance = {}
        for quiz in self.quiz_results:
            topic_key = f"{quiz['subject']} - {quiz['topic']}"
            if topic_key not in topic_performance:
                topic_performance[topic_key] = []
            topic_performance[topic_key].append(quiz['percentage'])
        
        # Identify topics with low average scores (below 60%)
        for topic, scores in topic_performance.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 60:
                weak_areas.append({
                    'topic': topic,
                    'average_score': round(avg_score, 1),
                    'attempts': len(scores),
                    'recommendation': 'Needs more practice and review'
                })
        
        # Sort by lowest score first
        weak_areas.sort(key=lambda x: x['average_score'])
        
        return weak_areas
    
    def generate_progress_report(self, student_name: str) -> str:
        """Generate a comprehensive progress report"""
        
        report_lines = []
        report_lines.append(f"📊 LEARNING PROGRESS REPORT")
        report_lines.append(f"=" * 50)
        report_lines.append(f"👤 Student Name: {student_name}")
        report_lines.append(f"📅 Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        report_lines.append("")
        
        # Topics studied summary
        report_lines.append("📚 TOPICS STUDIED")
        report_lines.append("-" * 30)
        if self.topics_studied:
            subjects = {}
            for topic in self.topics_studied:
                subject = topic['subject']
                if subject not in subjects:
                    subjects[subject] = []
                subjects[subject].append(f"  • {topic['topic']} ({topic['date']})")
            
            for subject, topics in subjects.items():
                report_lines.append(f"\n📘 {subject}:")
                report_lines.extend(topics)
        else:
            report_lines.append("No topics studied yet.")
        
        report_lines.append("\n")
        
        # Quiz performance summary
        quiz_summary = self.get_quiz_performance_summary()
        report_lines.append("📝 QUIZ PERFORMANCE")
        report_lines.append("-" * 30)
        report_lines.append(f"Total Quizzes Taken: {quiz_summary['total_quizzes']}")
        report_lines.append(f"Average Score: {quiz_summary['average_score']}%")
        
        if quiz_summary['best_subject']:
            report_lines.append(f"🏆 Strongest Subject: {quiz_summary['best_subject'][0]} ({quiz_summary['best_subject'][1]:.1f}%)")
        
        if quiz_summary['weakest_subject']:
            report_lines.append(f"📈 Needs Improvement: {quiz_summary['weakest_subject'][0]} ({quiz_summary['weakest_subject'][1]:.1f}%)")
        
        if quiz_summary['improvement_trend'] is not None:
            trend = "📈 Improving" if quiz_summary['improvement_trend'] > 0 else "📉 Declining"
            report_lines.append(f"Trend: {trend} ({quiz_summary['improvement_trend']:+.1f}%)")
        
        report_lines.append("")
        
        # Learning streaks
        streaks = self.get_learning_streaks()
        report_lines.append("🔥 LEARNING CONSISTENCY")
        report_lines.append("-" * 30)
        report_lines.append(f"Current Study Streak: {streaks['current_streak']} days")
        report_lines.append(f"Total Study Days: {streaks['study_days']}")
        report_lines.append(f"Total Topics Completed: {streaks['total_topics']}")
        report_lines.append("")
        
        # Weak areas
        weak_areas = self.identify_weak_areas()
        if weak_areas:
            report_lines.append("⚠️ AREAS FOR IMPROVEMENT")
            report_lines.append("-" * 30)
            for area in weak_areas[:5]:  # Top 5 weak areas
                report_lines.append(f"• {area['topic']}: {area['average_score']}% (attempted {area['attempts']} times)")
            report_lines.append("")
        
        # Study recommendations
        report_lines.append("🎯 PERSONALIZED RECOMMENDATIONS")
        report_lines.append("-" * 30)
        
        if quiz_summary['average_score'] >= 80:
            report_lines.append("🌟 Excellent work! You're mastering the concepts well.")
            report_lines.append("💡 Try tackling more advanced topics or help others learn.")
        elif quiz_summary['average_score'] >= 60:
            report_lines.append("👍 Good progress! Keep up the consistent practice.")
            report_lines.append("💡 Focus on weak areas and review regularly.")
        else:
            report_lines.append("📚 Keep practicing! Learning takes time and patience.")
            report_lines.append("💡 Spend more time on topic explanations before taking quizzes.")
        
        if weak_areas:
            report_lines.append(f"🔍 Priority Review: {weak_areas[0]['topic']}")
        
        if streaks['current_streak'] == 0:
            report_lines.append("⏰ Try to study a little bit every day for better retention.")
        else:
            report_lines.append(f"🔥 Great job maintaining a {streaks['current_streak']}-day study streak!")
        
        report_lines.append("")
        report_lines.append("🚀 NEXT STEPS")
        report_lines.append("-" * 30)
        report_lines.append("1. Review weak areas identified above")
        report_lines.append("2. Practice more quizzes on challenging topics")
        report_lines.append("3. Use the Q&A feature to clarify doubts")
        report_lines.append("4. Watch educational videos for visual learning")
        report_lines.append("5. Maintain consistent daily study habits")
        report_lines.append("")
        report_lines.append("Keep learning and growing! 🌟")
        report_lines.append("")
        report_lines.append(f"Report generated by AI Learning Assistant")
        report_lines.append(f"AP State Board Syllabus Learning Platform")
        
        return "\n".join(report_lines)
    
    def export_data(self) -> Dict[str, Any]:
        """Export all student data for backup or analysis"""
        return {
            'topics_studied': self.topics_studied,
            'quiz_results': self.quiz_results,
            'chat_interactions': self.chat_interactions,
            'video_views': self.video_views,
            'study_sessions': self.study_sessions,
            'export_timestamp': datetime.now().isoformat()
        }
    
    def import_data(self, data: Dict[str, Any]):
        """Import student data from backup"""
        self.topics_studied = data.get('topics_studied', [])
        self.quiz_results = data.get('quiz_results', [])
        self.chat_interactions = data.get('chat_interactions', [])
        self.video_views = data.get('video_views', [])
        self.study_sessions = data.get('study_sessions', [])
    
    def generate_pdf_report(self, student_name: str) -> bytes:
        """Generate a comprehensive PDF learning report"""
        
        # Create a BytesIO buffer to hold PDF data
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1f4e79')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#2e5984')
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=14
        )
        
        # Title
        title = Paragraph("🎓 AI Learning Assistant", title_style)
        subtitle = Paragraph("Student Learning Progress Report", heading_style)
        story.append(title)
        story.append(subtitle)
        story.append(Spacer(1, 20))
        
        # Student Information
        student_info = [
            ["Student Name:", student_name],
            ["Report Date:", datetime.now().strftime('%B %d, %Y')],
            ["Report Time:", datetime.now().strftime('%I:%M %p')],
            ["Platform:", "AP State Board Syllabus Learning Platform"]
        ]
        
        info_table = Table(student_info, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Overview Statistics
        overview_heading = Paragraph("📊 Learning Overview", heading_style)
        story.append(overview_heading)
        
        topics_count = len(self.topics_studied)
        quizzes_count = len(self.quiz_attempts)
        videos_count = len(self.video_views)
        avg_score = sum(q['score'] for q in self.quiz_attempts) / len(self.quiz_attempts) if self.quiz_attempts else 0
        
        overview_data = [
            ["Metric", "Value"],
            ["Topics Studied", str(topics_count)],
            ["Quizzes Taken", str(quizzes_count)],
            ["Videos Watched", str(videos_count)],
            ["Average Quiz Score", f"{avg_score:.1f}%"]
        ]
        
        overview_table = Table(overview_data, colWidths=[2.5*inch, 2.5*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472c4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ]))
        
        story.append(overview_table)
        story.append(Spacer(1, 20))
        
        # Topics Studied Section
        if self.topics_studied:
            topics_heading = Paragraph("📚 Topics Studied", heading_style)
            story.append(topics_heading)
            
            # Group topics by subject
            subjects_topics = {}
            for topic in self.topics_studied:
                subject = topic['subject']
                if subject not in subjects_topics:
                    subjects_topics[subject] = []
                subjects_topics[subject].append(topic)
            
            topics_data = [["Subject", "Topic", "Chapter", "Date"]]
            
            for subject, topics in subjects_topics.items():
                for i, topic in enumerate(topics[-10:]):  # Last 10 topics per subject
                    row = [
                        subject if i == 0 else "",  # Show subject only once
                        topic['topic'],
                        topic['chapter'], 
                        topic['date']
                    ]
                    topics_data.append(row)
            
            topics_table = Table(topics_data, colWidths=[1.2*inch, 2*inch, 1.5*inch, 1*inch])
            topics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#70ad47')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ]))
            
            story.append(topics_table)
            story.append(Spacer(1, 20))
        
        # Quiz Performance Section
        if self.quiz_attempts:
            quiz_heading = Paragraph("📝 Quiz Performance", heading_style)
            story.append(quiz_heading)
            
            quiz_data = [["Topic", "Quiz Type", "Score", "Questions", "Date"]]
            
            # Show last 15 quiz attempts
            recent_quizzes = self.quiz_attempts[-15:]
            for quiz in recent_quizzes:
                row = [
                    quiz['topic'][:20] + "..." if len(quiz['topic']) > 20 else quiz['topic'],
                    quiz['quiz_type'],
                    f"{quiz['score']:.1f}%",
                    f"{quiz['correct_answers']}/{quiz['total_questions']}",
                    quiz['date']
                ]
                quiz_data.append(row)
            
            quiz_table = Table(quiz_data, colWidths=[1.8*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch])
            quiz_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ]))
            
            story.append(quiz_table)
            story.append(Spacer(1, 20))
        
        # Performance Analysis
        analysis_heading = Paragraph("📈 Performance Analysis", heading_style)
        story.append(analysis_heading)
        
        if self.quiz_attempts:
            # Calculate subject-wise performance
            subject_performance = {}
            for quiz in self.quiz_attempts:
                # Extract subject from topic context (simplified)
                if 'Math' in quiz['topic'] or 'Number' in quiz['topic']:
                    subject = 'Mathematics'
                elif 'Science' in quiz['topic'] or 'Plant' in quiz['topic'] or 'Animal' in quiz['topic']:
                    subject = 'Science'
                else:
                    subject = 'Environmental Studies'
                
                if subject not in subject_performance:
                    subject_performance[subject] = []
                subject_performance[subject].append(quiz['score'])
            
            analysis_data = [["Subject", "Avg Score", "Attempts", "Status"]]
            
            for subject, scores in subject_performance.items():
                avg_score = sum(scores) / len(scores)
                attempts = len(scores)
                
                if avg_score >= 80:
                    status = "Excellent ⭐"
                elif avg_score >= 70:
                    status = "Good 👍"
                elif avg_score >= 60:
                    status = "Fair 📚"
                else:
                    status = "Needs Work 💪"
                
                analysis_data.append([subject, f"{avg_score:.1f}%", str(attempts), status])
            
            analysis_table = Table(analysis_data, colWidths=[2*inch, 1*inch, 1*inch, 1.5*inch])
            analysis_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ]))
            
            story.append(analysis_table)
            story.append(Spacer(1, 20))
        
        # Recommendations
        recommendations_heading = Paragraph("💡 Learning Recommendations", heading_style)
        story.append(recommendations_heading)
        
        recommendations = []
        
        if avg_score >= 80:
            recommendations.extend([
                "• Excellent performance! Continue your current study approach",
                "• Consider exploring advanced topics in your strong subjects",
                "• Help other students - teaching reinforces your own learning"
            ])
        elif avg_score >= 60:
            recommendations.extend([
                "• Good progress! Focus on improving weaker areas",
                "• Review topics where you scored below 70%",
                "• Use the mini quiz feature for more practice"
            ])
        else:
            recommendations.extend([
                "• Focus on understanding fundamental concepts",
                "• Spend more time on topic explanations before quizzes",
                "• Use video learning for visual understanding"
            ])
        
        recommendations.extend([
            "• Maintain consistent daily study habits",
            "• Take breaks between study sessions",
            "• Ask questions using the interactive Q&A feature"
        ])
        
        for rec in recommendations:
            rec_para = Paragraph(rec, normal_style)
            story.append(rec_para)
        
        story.append(Spacer(1, 20))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        
        footer = Paragraph(
            "Generated by AI Learning Assistant - AP State Board Syllabus Learning Platform<br/>" +
            f"Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            footer_style
        )
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data from buffer
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
