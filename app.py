"""
AI-Powered Student Learning App
Designed for AP State Board Syllabus (Classes 1-10)
Updated with Continuous Adaptive Quiz System
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, List, Any
import random

# Import visualization library
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Import custom modules
from curriculum_data import get_curriculum_data
from ai_assistant import AIAssistant
from quiz_generator import QuizGenerator
from video_recommender import VideoRecommender
from student_history import StudentHistory
from user_preferences import learning_preferences_survey, get_user_preferences, create_user_profile_summary

# Import OCR functionality for writing quiz
try:
    from OCRapp import ExamAssistant
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="🎓 AI Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure MathJax for LaTeX rendering
st.markdown("""
<script>
    window.MathJax = {
        tex: {
            inlineMath: [['$', '$']],
            displayMath: [['$$', '$$']],
            processEscapes: true,
            processEnvironments: true,
            packages: ['base', 'ams', 'noerrors', 'noundefined', 'autoload', 'physics'],
            macros: {
                // Improved fraction macro
                "frac": ["\\frac{#1}{#2}", 2],
                // Vector notation
                "vec": ["\\boldsymbol{\\mathbf{#1}}", 1],
                // Derivative
                "dv": ["\\frac{d#1}{d#2}", 2],
                // Partial derivative
                "pdv": ["\\frac{\\partial #1}{\\partial #2}", 2]
            }
        },
        options: {
            ignoreHtmlClass: 'tex2jax_ignore',
            processHtmlClass: 'tex2jax_process',
            renderActions: {
                findScript: [10, function (doc) {
                    document.querySelectorAll('script[type^="math/tex"]').forEach(function(node) {
                        var display = !!node.type.match(/; *mode=display/);
                        var math = new doc.options.MathItem(node.textContent, doc.inputJax[0], display);
                        var text = document.createTextNode('');
                        node.parentNode.replaceChild(text, node);
                        math.start = {node: text, delim: '', n: 0};
                        math.end = {node: text, delim: '', n: 0};
                        doc.math.push(math);
                    });
                }, '']
            }
        },
        svg: {
            fontCache: 'global',
            scale: 1.1,
            minScale: 0.5
        },
        loader: {
            load: ['[tex]/physics']
        },
        startup: {
            typeset: true
        }
    };
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    
    # Authentication and user data
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ""
    if 'selected_class' not in st.session_state:
        st.session_state.selected_class = None
    if 'selected_subject' not in st.session_state:
        st.session_state.selected_subject = None
    if 'selected_chapter' not in st.session_state:
        st.session_state.selected_chapter = None
    if 'selected_topic' not in st.session_state:
        st.session_state.selected_topic = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "authentication"
    if 'survey_data' not in st.session_state:
        st.session_state.survey_data = {}
    
    # Chat and interaction
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'popup_chat_history' not in st.session_state:
        st.session_state.popup_chat_history = []
    if 'current_explanation' not in st.session_state:
        st.session_state.current_explanation = None
    
    # Quiz system
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    
    # Continuous adaptive quiz
    if 'continuous_quiz_active' not in st.session_state:
        st.session_state.continuous_quiz_active = False
    if 'continuous_quiz_difficulty' not in st.session_state:
        st.session_state.continuous_quiz_difficulty = "easy"
    if 'continuous_quiz_stats' not in st.session_state:
        st.session_state.continuous_quiz_stats = {
            'total_questions': 0,
            'correct_answers': 0,
            'consecutive_correct': 0,
            'consecutive_wrong': 0,
            'question_history': [],
            'last_wrong_concept': None
        }
    if 'current_adaptive_question' not in st.session_state:
        st.session_state.current_adaptive_question = None
    if 'show_feedback' not in st.session_state:
        st.session_state.show_feedback = False
    if 'last_answer_correct' not in st.session_state:
        st.session_state.last_answer_correct = None
    if 'last_question' not in st.session_state:
        st.session_state.last_question = None
    if 'last_selected_answer' not in st.session_state:
        st.session_state.last_selected_answer = None
    
    # Final quiz system
    if 'final_quiz_active' not in st.session_state:
        st.session_state.final_quiz_active = False
    if 'final_quiz_questions' not in st.session_state:
        st.session_state.final_quiz_questions = []
    if 'final_quiz_answers' not in st.session_state:
        st.session_state.final_quiz_answers = {}
    if 'final_quiz_submitted' not in st.session_state:
        st.session_state.final_quiz_submitted = False
    if 'final_quiz_score' not in st.session_state:
        st.session_state.final_quiz_score = 0
    if 'final_quiz_detailed_results' not in st.session_state:
        st.session_state.final_quiz_detailed_results = []
    
    # Popup and interaction states
    if 'show_qa_popup' not in st.session_state:
        st.session_state.show_qa_popup = False
    if 'show_hint_popup' not in st.session_state:
        st.session_state.show_hint_popup = False
    if 'hint_chat_history' not in st.session_state:
        st.session_state.hint_chat_history = []
    if 'current_hint_question' not in st.session_state:
        st.session_state.current_hint_question = None
    if 'hint_level' not in st.session_state:
        st.session_state.hint_level = 0
    if 'current_menu_option' not in st.session_state:
        st.session_state.current_menu_option = None
    
    # Writing quiz system
    if 'writing_quiz_active' not in st.session_state:
        st.session_state.writing_quiz_active = False
    if 'writing_quiz_question' not in st.session_state:
        st.session_state.writing_quiz_question = None
    if 'writing_quiz_marks' not in st.session_state:
        st.session_state.writing_quiz_marks = 2
    if 'writing_quiz_evaluations' not in st.session_state:
        st.session_state.writing_quiz_evaluations = []
    if 'show_evaluation_results' not in st.session_state:
        st.session_state.show_evaluation_results = False
    if 'evaluation_image' not in st.session_state:
        st.session_state.evaluation_image = None
    if 'evaluation_question' not in st.session_state:
        st.session_state.evaluation_question = None
    if 'evaluation_marks' not in st.session_state:
        st.session_state.evaluation_marks = None
    
    # Final writing quiz system
    if 'final_writing_quiz_active' not in st.session_state:
        st.session_state.final_writing_quiz_active = False
    if 'final_writing_quiz_questions' not in st.session_state:
        st.session_state.final_writing_quiz_questions = []
    if 'final_writing_quiz_answers' not in st.session_state:
        st.session_state.final_writing_quiz_answers = {}
    if 'final_writing_quiz_submitted' not in st.session_state:
        st.session_state.final_writing_quiz_submitted = False
    if 'final_writing_quiz_current_index' not in st.session_state:
        st.session_state.final_writing_quiz_current_index = 0
    if 'final_writing_quiz_evaluations' not in st.session_state:
        st.session_state.final_writing_quiz_evaluations = {}
    if 'final_writing_quiz_evaluation_in_progress' not in st.session_state:
        st.session_state.final_writing_quiz_evaluation_in_progress = set()
    if 'evaluation_start_times' not in st.session_state:
        st.session_state.evaluation_start_times = {}
    
    # Student history
    if 'student_history' not in st.session_state:
        st.session_state.student_history = StudentHistory()

def authentication_page():
    """Authentication page for API key and student details"""
    st.title("🎓 Welcome to AI Learning Assistant")
    st.subheader("🏛️ AP State Board Syllabus Learning Platform")
    
    with st.form("auth_form"):
        st.markdown("### 🔐 Authentication")
        
        col1, col2 = st.columns(2)
        
        with col1:
            student_name = st.text_input("👤 Student Name", placeholder="Enter your name")
        
        with col2:
            api_key = st.text_input("🔑 OpenAI API Key", type="password", 
                                  placeholder="sk-...")
        
        st.markdown("---")
        st.markdown("**📝 Note:** Your API key is kept secure and only used for generating educational content.")
        
        submit_button = st.form_submit_button("🚀 Start Learning Journey")
        
        if submit_button:
            if student_name.strip() and api_key.strip():
                st.session_state.student_name = student_name.strip()
                st.session_state.api_key = api_key.strip()
                st.session_state.current_page = "preferences_survey"
                st.rerun()
            else:
                st.error("⚠️ Please provide both your name and OpenAI API key.")

def preferences_survey_page():
    """Learning preferences survey page"""
    st.title(f"👋 Welcome {st.session_state.student_name}!")
    st.subheader("🎯 Let's Personalize Your Learning Experience")
    
    learning_preferences_survey()
    
    # Add a "Continue" button if preferences have been saved
    if st.session_state.get('survey_data'):
        if st.button("▶️ Continue to Class Selection", type="primary"):
            st.session_state.current_page = "class_selection"
            st.rerun()

def class_selection_page():
    """Class selection page"""
    st.title(f"👋 Welcome {st.session_state.student_name}!")
    st.subheader("📚 Select Your Class")
    
    curriculum = get_curriculum_data()
    
    col1, col2, col3 = st.columns(3)
    
    classes = list(curriculum.keys())
    
    for i, class_name in enumerate(classes):
        col = [col1, col2, col3][i % 3]
        
        with col:
            if st.button(f"📖 {class_name}", key=f"class_{i}", use_container_width=True):
                st.session_state.selected_class = class_name
                st.session_state.current_page = "subject_selection"
                st.rerun()

def subject_selection_page():
    """Subject selection page"""
    st.title(f"📚 {st.session_state.selected_class}")
    st.subheader("🎯 Choose Your Subject")
    
    curriculum = get_curriculum_data()
    subjects = curriculum[st.session_state.selected_class]
    
    col1, col2 = st.columns(2)
    
    for i, subject in enumerate(subjects.keys()):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            if st.button(f"📘 {subject}", key=f"subject_{i}", use_container_width=True):
                st.session_state.selected_subject = subject
                st.session_state.current_page = "chapter_selection"
                st.rerun()
    
    if st.button("⬅️ Back to Class Selection", key="back_to_class_selection"):
        st.session_state.current_page = "class_selection"
        st.session_state.selected_class = None
        st.rerun()

def chapter_selection_page():
    """Chapter selection page"""
    st.title(f"📖 {st.session_state.selected_class} - {st.session_state.selected_subject}")
    st.subheader("📑 Select Chapter")
    
    curriculum = get_curriculum_data()
    chapters = curriculum[st.session_state.selected_class][st.session_state.selected_subject]
    
    for i, chapter in enumerate(chapters.keys()):
        if st.button(f"📄 {chapter}", key=f"chapter_{i}", use_container_width=True):
            st.session_state.selected_chapter = chapter
            st.session_state.current_page = "topic_selection"
            st.rerun()
    
    if st.button("⬅️ Back to Subject Selection", key="back_to_subject_selection"):
        st.session_state.current_page = "subject_selection"
        st.session_state.selected_subject = None
        st.rerun()

def topic_selection_page():
    """Topic selection page"""
    st.title(f"📚 {st.session_state.selected_subject} - {st.session_state.selected_chapter}")
    st.subheader("🎯 Choose Your Topic")
    
    curriculum = get_curriculum_data()
    topics = curriculum[st.session_state.selected_class][st.session_state.selected_subject][st.session_state.selected_chapter]
    
    for i, topic in enumerate(topics):
        if st.button(f"📝 {topic}", key=f"topic_{i}", use_container_width=True):
            st.session_state.selected_topic = topic
            st.session_state.current_page = "learning_hub"
            # Reset chat history for new topic
            st.session_state.chat_history = []
            # Reset explanation for new topic
            st.session_state.current_explanation = None
            # Reset continuous quiz state for new topic
            if 'continuous_quiz_active' in st.session_state:
                st.session_state.continuous_quiz_active = False
                st.session_state.continuous_quiz_stats = {
                    'total_questions': 0,
                    'correct_answers': 0,
                    'consecutive_correct': 0,
                    'consecutive_wrong': 0,
                    'question_history': [],
                    'last_wrong_concept': None
                }
                st.session_state.current_adaptive_question = None
                st.session_state.show_feedback = False
            st.rerun()
    
    if st.button("⬅️ Back to Chapter Selection", key="back_to_chapter_selection"):
        st.session_state.current_page = "chapter_selection"
        st.session_state.selected_chapter = None
        st.rerun()

def learning_hub_page():
    """Main learning hub with all features"""
    st.title(f"🎓 Learning: {st.session_state.selected_topic}")
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Learning Menu")
        
        menu_option = st.radio(
            "Choose learning mode:",
            ["📖 Topic Explanation", "🌐 3D Model Viewer", "💬 Interactive Q&A", "🎥 Video Learning", 
             "🧩 Mini Quiz", "📝 Final Quiz", "📊 My Progress"]
        )
        
        st.markdown("---")
        if st.button("🏠 Back to Topics", key="back_to_topics"):
            st.session_state.current_page = "topic_selection"
            st.session_state.selected_topic = None
            # Reset explanation when leaving topic
            st.session_state.current_explanation = None
            # Reset quiz states when leaving topic
            if 'continuous_quiz_active' in st.session_state:
                st.session_state.continuous_quiz_active = False
            st.rerun()
    
    # Reset popup states when menu option changes
    if st.session_state.get('current_menu_option') != menu_option:
        st.session_state.show_qa_popup = False
        st.session_state.show_hint_popup = False
        st.session_state.current_menu_option = menu_option
    
    # Main content area
    if menu_option == "📖 Topic Explanation":
        topic_explanation_section()
    elif menu_option == "💬 Interactive Q&A":
        interactive_qa_section()
    elif menu_option == "🎥 Video Learning":
        video_learning_section()
    elif menu_option == "🧩 Mini Quiz":
        mini_quiz_section()
    elif menu_option == "📝 Final Quiz":
        final_quiz_section()
    elif menu_option == "📊 My Progress":
        progress_section()
    elif menu_option == "🌐 3D Model Viewer":
        # Direct redirect without intermediate page
        st.components.v1.html("""
        <script>
        window.open('https://www.learningpadedu.com/', '_blank');
        </script>
        """, height=0)
        st.success("🌐 Opening 3D Model Viewer in a new tab...")
        st.info("💡 If the website didn't open automatically, [click here](https://www.learningpadedu.com/)")

def topic_explanation_section():
    """Topic explanation section"""
    st.subheader("📖 Topic Explanation")
    
    # Custom CSS for red buttons
    st.markdown("""
    <style>
    .stButton > button[kind="primary"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #ff3030 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create two columns for the main button and popup button
    col1, col2 = st.columns([3, 1])
    
    with col1:
        generate_explanation = st.button("🎯 Generate Explanation", type="primary", key="generate_explanation")
    
    with col2:
        open_qa_popup = st.button("🤖 AI Assistant", type="primary", help="Ask questions about this topic in a popup", key="open_ai_assistant")
    
    # Handle explanation generation
    if generate_explanation:
        with st.spinner("🤖 AI is preparing your personalized lesson..."):
            ai_assistant = AIAssistant(st.session_state.api_key)
            
            # Get user preferences if available
            user_preferences = get_user_preferences()
            
            # Check if current subject requires LaTeX formatting
            is_math_science = st.session_state.selected_subject.lower() in [
                'mathematics', 'math', 'maths', 
                'physical science', 'physics', 'science', 'physical sciences'
            ]
            
            # Generate the explanation
            explanation = ai_assistant.generate_topic_explanation(
                topic=st.session_state.selected_topic,
                subject=st.session_state.selected_subject,
                class_level=st.session_state.selected_class,
                user_preferences=user_preferences
            )
            
            if is_math_science:
                # Add LaTeX formatting guide and validation section
                latex_guide = """
### 📐 Mathematical & Scientific Notation Guide

This lesson uses LaTeX formatting for precise mathematical and scientific notation:

- **Display Equations**: Centered, larger formulas use double dollar signs:
  $$formula$$

- **Inline Math**: Mathematical expressions within text use single dollar signs:
  $formula$

- **Units & Dimensions**: All units are properly formatted:
  - $m/s^2$ for acceleration
  - $kg$ for mass
  - $N$ for force
  - $J$ for energy
  - $W$ for power

- **Common Notation**:
  - Fractions: $$\\frac{numerator}{denominator}$$
  - Powers: $x^2$, $y^3$
  - Square roots: $$\\sqrt{x}$$
  - Greek letters: $\\alpha$, $\\beta$, $\\theta$
  - Vectors: $$\\vec{F}$$
  - Derivatives: $$\\frac{d}{dx}$$
  - Integrals: $$\\int_{a}^{b}$$

---
"""
                # Add the LaTeX guide after the main content
                explanation = f"{explanation}\n\n{latex_guide}"
            
            # Store explanation in session state
            st.session_state.current_explanation = explanation
            
            # Record this study session
            st.session_state.student_history.add_topic_studied(
                st.session_state.selected_class,
                st.session_state.selected_subject,
                st.session_state.selected_chapter,
                st.session_state.selected_topic
            )
    
    # Display explanation if it exists
    if st.session_state.current_explanation:
        st.markdown("### 📚 Lesson Content")
        
        # Check if current subject requires LaTeX formatting
        is_math_science = st.session_state.selected_subject.lower() in [
            'mathematics', 'math', 'maths', 
            'physical science', 'physics', 'science', 'physical sciences'
        ]
        
        if is_math_science:
            # Add enhanced LaTeX styling
            st.markdown("""
            <style>
                /* Enhanced LaTeX/MathJax styling */
                .math-content {
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                }
                
                /* Display equations */
                .katex-display {
                    margin: 1.5em 0 !important;
                    padding: 10px !important;
                    background-color: #f0f8ff !important;
                    border-radius: 8px !important;
                    border-left: 4px solid #0066cc !important;
                    overflow-x: auto !important;
                }
                
                /* Enhanced fraction display */
                .katex-display .mfrac {
                    margin: 0 0.2em !important;
                }
                
                .katex-display .mfrac .frac-line {
                    border-color: #0066cc !important;
                }
                
                .katex-display .mfrac .mspace {
                    margin-top: 0.1em !important;
                    margin-bottom: 0.1em !important;
                }
                
                /* Better spacing for numerators and denominators */
                .katex .mfrac .mspace {
                    margin-top: 0.1em !important;
                    margin-bottom: 0.1em !important;
                }
                
                /* Inline math */
                .katex {
                    font-size: 1.1em !important;
                    color: #0066cc !important;
                }
                
                /* Better fraction sizing for inline math */
                .katex .mfrac {
                    vertical-align: -0.5em !important;
                }
                
                /* Improved fraction line */
                .katex .frac-line {
                    min-height: 1px !important;
                    border-bottom-width: 1px !important;
                }
                
                /* Step-by-step solutions */
                .math-step {
                    background-color: #e9ecef;
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 5px;
                    border-left: 3px solid #6c757d;
                }
                
                /* Scientific units */
                .math-units {
                    color: #28a745;
                    font-style: italic;
                }
                
                /* Important formulas */
                .important-formula {
                    background-color: #fff3cd;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 8px;
                    border-left: 4px solid #ffc107;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Add LaTeX rendering info with examples
            st.info("""
            💡 **Mathematical & Scientific Notation**:
            - Display equations are centered and boxed (e.g., $$F = ma$$)
            - Inline math is highlighted (e.g., $E = mc^2$)
            - Units are properly formatted (e.g., $m/s^2$, $kg$)
            - Step-by-step solutions are clearly structured
            """)
        
        # Create a container for the content with proper styling
        with st.container():
            if is_math_science:
                st.markdown('<div class="math-content">', unsafe_allow_html=True)
                st.markdown(st.session_state.current_explanation, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Force MathJax to re-render
                st.markdown("""
                <script>
                    if (window.MathJax) {
                        window.MathJax.typesetPromise && window.MathJax.typesetPromise();
                    }
                </script>
                """, unsafe_allow_html=True)
            else:
                # Standard rendering for non-math subjects
                st.markdown(st.session_state.current_explanation, unsafe_allow_html=True)
    
    # Handle Q&A popup
    if open_qa_popup:
        st.session_state.show_qa_popup = True
    
    # Initialize popup state if not exists
    if 'show_qa_popup' not in st.session_state:
        st.session_state.show_qa_popup = False
    
    # Show Q&A popup dialog
    if st.session_state.show_qa_popup:
        show_qa_popup_dialog()

@st.dialog("🤖 AI Assistant", width="large")
def show_qa_popup_dialog():
    """Popup dialog for interactive Q&A about the current topic"""
    
    # Initialize popup chat history if not exists
    if 'popup_chat_history' not in st.session_state:
        st.session_state.popup_chat_history = []
    
    # Display current topic info
    topic_title = st.session_state.get('selected_topic', 'Unknown Topic')
    subject_info = st.session_state.get('selected_subject', 'Unknown Subject')
    class_info = st.session_state.get('selected_class', 'Unknown Class')
    
    st.markdown(f"**🎯 Current Topic:** {topic_title}")
    st.markdown(f"**📚 Subject:** {subject_info} ({class_info})")
    st.markdown("---")
    
    # Display popup chat history in a container with max height
    chat_container = st.container(height=300)
    with chat_container:
        if not st.session_state.popup_chat_history:
            st.info("👋 Ask me anything about this topic! I'm here to help you understand better.")
        else:
            for message in st.session_state.popup_chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    
    # Chat input for popup
    popup_prompt = st.chat_input("Ask your question about the topic...", key="popup_chat_input")
    
    if popup_prompt:
        # Add user message to popup chat history
        st.session_state.popup_chat_history.append({"role": "user", "content": popup_prompt})
        
        # Generate AI response
        with st.spinner("🤔 Thinking..."):
            ai_assistant = AIAssistant(st.session_state.api_key)
            
            response = ai_assistant.answer_question(
                question=popup_prompt,
                topic=st.session_state.selected_topic,
                subject=st.session_state.selected_subject,
                class_level=st.session_state.selected_class
            )
            
            # Add assistant response to popup chat history
            st.session_state.popup_chat_history.append({"role": "assistant", "content": response})
            
            # Record this interaction
            st.session_state.student_history.add_chat_interaction(
                st.session_state.selected_topic,
                popup_prompt,
                response
            )
        
        st.rerun()
    
    # Close button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_popup_chat"):
            st.session_state.popup_chat_history = []
            st.rerun()
    
    with col2:
        if st.button("📋 Copy to Main Chat", use_container_width=True, key="copy_to_main_chat"):
            # Copy popup chat to main chat history
            st.session_state.chat_history.extend(st.session_state.popup_chat_history)
            st.session_state.popup_chat_history = []
            st.success("✅ Chat copied to main Q&A section!")
            st.rerun()
    
    with col3:
        if st.button("❌ Close", use_container_width=True, key="close_qa_popup"):
            st.session_state.show_qa_popup = False
            st.rerun()

@st.dialog("💡 AI Tutor - Question Hint", width="large")
def show_hint_popup_dialog():
    """Popup dialog for interactive hints about the current quiz question"""
    
    # Initialize hint chat history if not exists
    if 'hint_chat_history' not in st.session_state:
        st.session_state.hint_chat_history = []
    
    question = st.session_state.current_hint_question
    
    # Display current question info
    st.markdown("**📝 Question:**")
    st.markdown(f"*{question['question']}*")
    st.markdown("---")
    
    # Display hint chat history in a container with max height
    chat_container = st.container(height=300)
    with chat_container:
        if not st.session_state.hint_chat_history:
            # Generate initial hint using AI based on the specific question
            with st.spinner("🤔 Generating your first hint..."):
                ai_assistant = AIAssistant(st.session_state.api_key)
                
                # Generate first hint for this specific question
                first_hint = ai_assistant.generate_interactive_hint(
                    question=question,
                    student_input="",  # Empty for first hint
                    hint_level=1,  # First hint level
                    subject=st.session_state.selected_subject,
                    class_level=st.session_state.selected_class,
                    topic=st.session_state.selected_topic
                )
                
                st.session_state.hint_chat_history.append({"role": "assistant", "content": first_hint})
                st.session_state.hint_level = 1  # Set initial hint level
            
            # Display the first hint
            with st.chat_message("assistant"):
                st.markdown(first_hint)
        else:
            for message in st.session_state.hint_chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    
    # Chat input for hints
    hint_prompt = st.chat_input("Share your thoughts or ask for the next hint...", key="hint_chat_input")
    
    if hint_prompt:
        # Add user message to hint chat history
        st.session_state.hint_chat_history.append({"role": "user", "content": hint_prompt})
        
        # Generate AI hint response
        with st.spinner("🤔 Generating next hint..."):
            ai_assistant = AIAssistant(st.session_state.api_key)
            
            # Increment hint level for next progressive hint
            st.session_state.hint_level += 1
            
            response = ai_assistant.generate_interactive_hint(
                question=question,
                student_input=hint_prompt,
                hint_level=st.session_state.hint_level,
                subject=st.session_state.selected_subject,
                class_level=st.session_state.selected_class,
                topic=st.session_state.selected_topic
            )
            
            # Add assistant response to hint chat history
            st.session_state.hint_chat_history.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🗑️ Clear Hints", use_container_width=True, key="clear_hints"):
            st.session_state.hint_chat_history = []
            st.session_state.hint_level = 0
            st.rerun()
    
    with col2:
        if st.button("🎯 Show Answer", use_container_width=True, key="show_answer_hint"):
            # Show the complete answer as final hint
            final_hint = f"""🎯 **Complete Answer:**

**Correct Answer:** {question['correct_answer']}

**Explanation:** {question.get('explanation', 'This is the correct answer for this question.')}

**Concept Focus:** {question.get('concept_focus', 'Understanding the key concept in this question.')}

Now that you know the answer, make sure you understand the reasoning behind it! 🧠"""
            
            st.session_state.hint_chat_history.append({"role": "assistant", "content": final_hint})
            st.rerun()
    
    with col3:
        if st.button("❌ Close", use_container_width=True, key="close_hint_popup"):
            st.session_state.show_hint_popup = False
            st.rerun()

def interactive_qa_section():
    """Interactive Q&A chat section"""
    st.subheader("💬 Interactive Q&A Chat")
    st.markdown("Ask any questions about the topic and get instant AI-powered answers!")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask your question about the topic..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                ai_assistant = AIAssistant(st.session_state.api_key)
                
                response = ai_assistant.answer_question(
                    question=prompt,
                    topic=st.session_state.selected_topic,
                    subject=st.session_state.selected_subject,
                    class_level=st.session_state.selected_class
                )
                
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})

def video_learning_section():
    """Video learning section - Shows SINGLE most relevant video"""
    st.subheader("🎥 Video Learning")
    st.markdown("Get the **most relevant educational video** for your current topic!")
    
    # Show current topic context
    st.info(f"📚 **Current Topic:** {st.session_state.selected_topic} ({st.session_state.selected_subject})")
    
    # Single button to find the best video
    if st.button("🎯 Find Best Educational Video", type="primary", use_container_width=True, key="find_best_video"):
        with st.spinner("🔍 Finding the most relevant educational video for you..."):
            try:
                video_recommender = VideoRecommender()
                
                # Get the single best video
                best_video = video_recommender.get_best_educational_video(
                    topic=st.session_state.selected_topic,
                    subject=st.session_state.selected_subject,
                    class_level=st.session_state.selected_class
                )
                
                if best_video:
                    st.session_state['best_video'] = best_video
                    st.success("✅ Found the perfect educational video for you!")
                    st.rerun()
                else:
                    st.error("❌ Could not find educational video. Please check your internet connection.")
                    
            except Exception as e:
                st.error(f"⚠️ Error finding video: {str(e)}")
                
                # Create manual fallback
                topic = st.session_state.selected_topic
                subject = st.session_state.selected_subject
                search_query = f"{topic} {subject} tutorial explanation"
                search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                
                fallback_video = {
                    'title': f"{topic} - {subject} Educational Tutorial",
                    'url': search_url,
                    'duration': "Educational Content",
                    'views': "Find Best Match",
                    'channel': "YouTube Search",
                    'thumbnail': '',
                    'description': f"Search for the best educational videos about {topic} in {subject}"
                }
                
                st.session_state['best_video'] = fallback_video
                st.info("🔄 Created targeted video search for you!")
                st.rerun()
    
    # Display the best video if found
    if 'best_video' in st.session_state and st.session_state['best_video']:
        video = st.session_state['best_video']
        
        st.markdown("---")
        st.markdown("### 🏆 **Most Relevant Educational Video**")
        
        # Create attractive video display
        with st.container():
            # Video thumbnail and details
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if video.get('thumbnail') and video['thumbnail'].startswith('http'):
                    try:
                        st.image(video['thumbnail'], width=200)
                    except:
                        st.markdown("🎥", help="Educational Video")
                else:
                    # Create a nice video placeholder
                    st.markdown("""
                    <div style='background: linear-gradient(45deg, #FF6B6B, #4ECDC4); 
                                height: 150px; width: 200px; border-radius: 10px; 
                                display: flex; align-items: center; justify-content: center; 
                                color: white; font-size: 30px; margin: 10px 0;'>
                        🎥
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"#### 📹 {video['title']}")
                st.markdown(f"**📺 Channel:** {video.get('channel', 'Educational')}")
                st.markdown(f"**⏱️ Duration:** {video.get('duration', 'Educational Content')}")
                st.markdown(f"**👀 Views:** {video.get('views', 'Educational')}")
                
                if video.get('description'):
                    st.markdown(f"**📄 About:** {video['description'][:100]}...")
        
        # Big prominent watch button
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("▶️ **WATCH THIS VIDEO**", type="primary", use_container_width=True, key="watch_video"):
                # Record video view in history
                st.session_state.student_history.add_video_view(
                    st.session_state.selected_topic,
                    video['title'],
                    video['url']
                )
                
                # Show video link prominently
                st.success("🔗 **Click the link below to watch the video:**")
                st.markdown(f"""
                <div style='background-color: #e1f5fe; padding: 20px; border-radius: 10px; text-align: center; margin: 10px 0;'>
                    <h3>🎥 Ready to Watch!</h3>
                    <a href='{video['url']}' target='_blank' style='background-color: #ff4444; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px;'>
                        ▶️ OPEN VIDEO IN YOUTUBE
                    </a>
                    <p style='margin-top: 15px; color: #495057; font-weight: 500;'>Click the red button above to open the video in a new tab</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Also show as regular link for backup
                st.markdown(f"**Backup Link:** [🎥 {video['title']}]({video['url']})")
        
        # Clear video button
        st.markdown("---")
        if st.button("🗑️ Find Different Video", key="find_different_video"):
            if 'best_video' in st.session_state:
                del st.session_state['best_video']
            st.rerun()
    
    else:
        # Show helpful guidance when no video is selected
        st.markdown("### 🎯 **How Video Learning Works**")
        
        with st.container():
            st.markdown("""
            1. **🔍 Smart Search** - AI finds the most relevant educational video for your topic
            2. **🏆 Best Match** - Only shows you the highest quality educational content  
            3. **▶️ Direct Access** - Click to watch the video on YouTube
            4. **📊 Progress Tracking** - Your video views are recorded in your learning history
            """)
        
        # Show what topic will be searched
        st.markdown("---")
        st.markdown("### 🎬 **Ready to Find Video For:**")
        
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.info(f"**📖 Topic:** {st.session_state.selected_topic}")
        with info_col2:
            st.info(f"**📚 Subject:** {st.session_state.selected_subject}")
        
        st.markdown("**Click the button above to find your perfect educational video!** 🚀")

def mini_quiz_section():
    """Mini Quiz section with two tabs - Multiple Choice and Writing Quiz"""
    st.subheader("🧩 Mini Quiz")
    
    # Create tabs for different quiz types
    tab1, tab2 = st.tabs(["📝 Multiple Choice Quiz", "✍️ Writing Quiz"])
    
    with tab1:
        multiple_choice_quiz_section()
    
    with tab2:
        writing_quiz_section()

def multiple_choice_quiz_section():
    """Continuous Adaptive Multiple Choice Quiz section"""
    st.markdown("**Keep practicing until you feel confident!** The AI will adapt questions based on your performance.")
    
    # Initialize session state for continuous quiz
    if 'continuous_quiz_active' not in st.session_state:
        st.session_state.continuous_quiz_active = False
        st.session_state.continuous_quiz_difficulty = "easy"
        st.session_state.continuous_quiz_stats = {
            'total_questions': 0,
            'correct_answers': 0,
            'consecutive_correct': 0,
            'consecutive_wrong': 0,
            'question_history': [],
            'last_wrong_concept': None
        }
        st.session_state.current_adaptive_question = None
        st.session_state.show_feedback = False
        st.session_state.last_answer_correct = None
        st.session_state.last_question = None
        st.session_state.last_selected_answer = None
    
    # Display current stats
    if st.session_state.continuous_quiz_active:
        stats = st.session_state.continuous_quiz_stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Questions Answered", stats['total_questions'])
        with col2:
            accuracy = (stats['correct_answers'] / max(stats['total_questions'], 1)) * 100
            st.metric("Accuracy", f"{accuracy:.1f}%")
        with col3:
            st.metric("Current Level", st.session_state.continuous_quiz_difficulty.title())
        with col4:
            st.metric("Streak", f"✅{stats['consecutive_correct']} / ❌{stats['consecutive_wrong']}")
    
    # Start/Continue Quiz Section
    if not st.session_state.continuous_quiz_active:
        # Quiz start section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🚀 Start Continuous Quiz", type="primary", use_container_width=True, key="start_continuous_quiz"):
                st.session_state.continuous_quiz_active = True
                st.session_state.show_feedback = False
                st.rerun()
        
        with col2:
            st.markdown("**📚 How it works:**")
            st.markdown("• Answer questions continuously")
            st.markdown("• Get instant feedback")
            st.markdown("• Questions adapt to your level")
            st.markdown("• Move to Final Quiz when ready")
        
    else:
        # Active quiz section
        conduct_continuous_adaptive_quiz()

def conduct_continuous_adaptive_quiz():
    """Conduct the continuous adaptive quiz"""
    
    # Generate new question if needed
    if st.session_state.current_adaptive_question is None and not st.session_state.show_feedback:
        generate_next_adaptive_question()
    
    # Show feedback if answer was just submitted
    if st.session_state.show_feedback:
        display_answer_feedback()
    
    # Show current question if available and no feedback is showing
    elif st.session_state.current_adaptive_question is not None:
        display_current_adaptive_question()
    
    # Always show control buttons
    display_quiz_controls()

def generate_next_adaptive_question():
    """Generate the next adaptive question based on performance"""
    
    with st.spinner(f"🎯 Generating {st.session_state.continuous_quiz_difficulty} question..."):
        try:
            quiz_generator = QuizGenerator(st.session_state.api_key)
            stats = st.session_state.continuous_quiz_stats
            
            # Generate next question
            question = quiz_generator.generate_next_adaptive_question(
                topic=st.session_state.selected_topic,
                subject=st.session_state.selected_subject,
                class_level=st.session_state.selected_class,
                difficulty=st.session_state.continuous_quiz_difficulty,
                previous_wrong_answer=stats.get('last_wrong_concept'),
                question_history=stats.get('question_history', [])
            )
            
            if question:
                st.session_state.current_adaptive_question = question
                # Add to question history
                stats['question_history'].append(question['question'])
                # Keep only last 10 questions in history
                if len(stats['question_history']) > 10:
                    stats['question_history'] = stats['question_history'][-10:]
            else:
                st.error("❌ Could not generate question. Please try again.")
                
        except Exception as e:
            st.error(f"⚠️ Error generating question: {str(e)}")

def display_current_adaptive_question():
    """Display the current adaptive question"""
    
    question = st.session_state.current_adaptive_question
    stats = st.session_state.continuous_quiz_stats
    
    st.markdown("---")
    st.markdown(f"### 📝 Question #{stats['total_questions'] + 1}")
    st.markdown(f"**Difficulty Level:** {st.session_state.continuous_quiz_difficulty.title()}")
    st.markdown("")
    
    # Question with hint button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"**{question['question']}**")
    
    with col2:
        if st.button("💡 Hint", use_container_width=True, key="get_hint"):
            st.session_state.show_hint_popup = True
            st.session_state.current_hint_question = question
            st.session_state.hint_level = 0
            st.session_state.hint_chat_history = []
            st.rerun()
    
    # Answer options
    selected_answer = st.radio(
        "Select your answer:", 
        question['options'], 
        key=f"adaptive_q_{stats['total_questions']}"
    )
    
    # Submit button only
    if st.button("✅ Submit Answer", type="primary", use_container_width=True, key="submit_adaptive_answer"):
        submit_adaptive_answer(selected_answer, question)
    
    # Show hint popup if requested
    if st.session_state.show_hint_popup:
        show_hint_popup_dialog()

def submit_adaptive_answer(selected_answer: str, question: Dict):
    """Process the submitted answer"""
    
    stats = st.session_state.continuous_quiz_stats
    is_correct = selected_answer == question['correct_answer']
    
    # Update stats
    stats['total_questions'] += 1
    if is_correct:
        stats['correct_answers'] += 1
        stats['consecutive_correct'] += 1
        stats['consecutive_wrong'] = 0
        stats['last_wrong_concept'] = None
    else:
        stats['consecutive_correct'] = 0
        stats['consecutive_wrong'] += 1
        stats['last_wrong_concept'] = question.get('concept_focus', question['question'])
    
    # Store answer results for feedback
    st.session_state.last_answer_correct = is_correct
    st.session_state.last_question = question
    st.session_state.last_selected_answer = selected_answer
    
    # Update difficulty based on performance
    quiz_generator = QuizGenerator(st.session_state.api_key)
    new_difficulty = quiz_generator.determine_next_difficulty(
        current_difficulty=st.session_state.continuous_quiz_difficulty,
        is_correct=is_correct,
        consecutive_correct=stats['consecutive_correct'],
        consecutive_wrong=stats['consecutive_wrong']
    )
    st.session_state.continuous_quiz_difficulty = new_difficulty
    
    # Show feedback
    st.session_state.show_feedback = True
    st.session_state.current_adaptive_question = None
    
    st.rerun()

def display_answer_feedback():
    """Display feedback for the last answer"""
    
    is_correct = st.session_state.last_answer_correct
    question = st.session_state.last_question
    selected_answer = st.session_state.last_selected_answer
    stats = st.session_state.continuous_quiz_stats
    
    st.markdown("---")
    
    # Show feedback
    if is_correct:
        st.success("🎉 **Correct!** Well done!")
        if stats['consecutive_correct'] >= 2:
            st.info(f"🔥 Great streak! You've got {stats['consecutive_correct']} correct in a row!")
    else:
        st.error("❌ **Incorrect.**")
        st.markdown(f"**Your answer:** {selected_answer}")
        st.markdown(f"**Correct answer:** {question['correct_answer']}")
    
    # Show explanation
    if question.get('explanation'):
        with st.expander("💡 Explanation"):
            st.markdown(question['explanation'])
    
    # Show difficulty change notification
    if stats['consecutive_correct'] >= 2 and st.session_state.continuous_quiz_difficulty != "easy":
        st.info(f"🎯 **Level Up!** Moving to {st.session_state.continuous_quiz_difficulty} questions!")
    elif stats['consecutive_wrong'] >= 2 and st.session_state.continuous_quiz_difficulty != "hard":
        st.info(f"📚 **Adjusting difficulty** to help you learn better!")
    
    # Continue button
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("➡️ Next Question", type="primary", key="next_question_feedback"):
            st.session_state.show_feedback = False
            st.rerun()
    
    with col2:
        if not is_correct:
            if st.button("🔄 More Practice on This Concept", key="more_practice_concept"):
                # Force a related question on the same concept
                stats['last_wrong_concept'] = question.get('concept_focus', question['question'])
                st.session_state.show_feedback = False
                st.rerun()

def display_quiz_controls():
    """Display quiz control buttons"""
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏁 I'm Ready for Final Quiz!", key="ready_for_final_quiz"):
            st.session_state.continuous_quiz_active = False
            st.session_state.current_adaptive_question = None
            st.session_state.show_feedback = False
            
            # Show final quiz recommendation
            stats = st.session_state.continuous_quiz_stats
            if stats['total_questions'] >= 5:
                accuracy = (stats['correct_answers'] / stats['total_questions']) * 100
                if accuracy >= 70:
                    st.success("🎉 Great job! You're ready for the Final Quiz!")
                    st.info("💡 **Tip:** Click on 'Final Quiz' in the sidebar to take the comprehensive test.")
                else:
                    st.warning("📚 Consider practicing a bit more before taking the Final Quiz.")
                    st.info(f"Current accuracy: {accuracy:.1f}% - Try to get above 70% for better preparation!")
            else:
                st.info("💡 **Tip:** Answer at least 5 questions before moving to the Final Quiz for better preparation!")
            
            st.rerun()
    
    with col2:
        if st.button("🔄 Restart Quiz", key="restart_continuous_quiz"):
            # Reset all quiz state
            st.session_state.continuous_quiz_active = False
            st.session_state.continuous_quiz_stats = {
                'total_questions': 0,
                'correct_answers': 0,
                'consecutive_correct': 0,
                'consecutive_wrong': 0,
                'question_history': [],
                'last_wrong_concept': None
            }
            st.session_state.continuous_quiz_difficulty = "easy"
            st.session_state.current_adaptive_question = None
            st.session_state.show_feedback = False
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Learning Hub", key="back_to_hub_continuous_quiz"):
            st.session_state.continuous_quiz_active = False
            st.session_state.current_adaptive_question = None
            st.session_state.show_feedback = False
            st.rerun()

def writing_quiz_section():
    """Writing Quiz section with OCR functionality"""
    st.markdown("**Practice your written answers!** Write your answers on paper and upload an image for AI evaluation.")
    
    # Check if OCR functionality is available
    if not OCR_AVAILABLE:
        st.error("❌ OCR functionality not available. Please ensure OCRapp.py is in the same directory.")
        return
    
    # Check if user has selected a topic
    if not st.session_state.selected_topic:
        st.warning("⚠️ Please select a topic first from the Learning Hub to generate writing questions.")
        return
    
    # Initialize writing quiz state
    if 'writing_quiz_active' not in st.session_state:
        st.session_state.writing_quiz_active = False
        st.session_state.writing_quiz_question = None
        st.session_state.writing_quiz_marks = 2
        st.session_state.writing_quiz_evaluations = []
    
    # Display current topic
    st.info(f"📚 **Current Topic:** {st.session_state.selected_topic}")
    st.info(f"📖 **Subject:** {st.session_state.selected_subject} | **Class:** {st.session_state.selected_class}")
    
    if not st.session_state.writing_quiz_active:
        # Quiz setup section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📝 **Generate Writing Question**")
            
            marks = st.selectbox(
                "Select question marks:",
                options=[2, 4, 8],
                index=0,  # Default to 2 marks
                help="Choose the mark allocation for the question"
            )
            st.session_state.writing_quiz_marks = marks
            
            if st.button("🎯 Generate Writing Question", type="primary", use_container_width=True, key="generate_writing_question"):
                generate_writing_question()
        
        with col2:
            st.markdown("### 💡 **How it works:**")
            st.markdown("• Get a question for your topic")
            st.markdown("• Write answer on paper")
            st.markdown("• Take a clear photo")
            st.markdown("• Upload for AI evaluation")
            st.markdown("• Get detailed feedback")
    
    else:
        # Active writing quiz section
        conduct_writing_quiz()

def generate_writing_question():
    """Generate a writing question for the selected topic"""
    
    with st.spinner(f"🎯 Generating {st.session_state.writing_quiz_marks}-mark question..."):
        try:
            # Use OCR assistant
            if OCR_AVAILABLE:
                assistant = ExamAssistant(st.session_state.api_key)
            else:
                assistant = None
            if not assistant:
                st.error("❌ OCR functionality not available. Please ensure OCRapp.py is in the same directory.")
                return
            
            # Debug information
            topic = st.session_state.selected_topic
            marks = st.session_state.writing_quiz_marks
            
            # Generate question based on selected topic
            question = assistant.generate_question(
                topic=topic,
                marks=marks
            )
            
            # Enhanced debugging for question generation
            if question and question.strip():
                st.session_state.writing_quiz_question = question.strip()
                st.session_state.writing_quiz_active = True
                st.rerun()
            else:
                st.error("❌ Could not generate question. Please try again.")
                # Debug information to help identify the issue
                with st.expander("🔧 Debug Information"):
                    st.write(f"**Topic:** {topic}")
                    st.write(f"**Marks:** {marks}")
                    st.write(f"**API Key Available:** {bool(st.session_state.api_key)}")
                    st.write(f"**OCR Available:** {OCR_AVAILABLE}")
                    st.write(f"**Question Response:** {repr(question)}")
                    
        except Exception as e:
            st.error(f"⚠️ Error generating question: {str(e)}")
            # Additional debug info for exceptions
            with st.expander("🔧 Debug Information"):
                st.write(f"**Topic:** {st.session_state.get('selected_topic', 'Not set')}")
                st.write(f"**Marks:** {st.session_state.get('writing_quiz_marks', 'Not set')}")
                st.write(f"**API Key Available:** {bool(st.session_state.get('api_key', ''))}")
                st.write(f"**Error Details:** {type(e).__name__}: {str(e)}")
                import traceback
                st.write(f"**Full Traceback:** {traceback.format_exc()}")

def conduct_writing_quiz():
    """Conduct the writing quiz with OCR evaluation"""
    
    question = st.session_state.writing_quiz_question
    marks = st.session_state.writing_quiz_marks
    
    st.markdown("---")
    st.markdown(f"### 📝 Writing Question ({marks} marks)")
    
    # Display question in a styled box
    st.markdown(f"""
    <div style="
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1a237e;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    ">
        <h4 style="color: #1a237e; margin-bottom: 1rem; font-weight: bold;">Question:</h4>
        <p style="color: #212529; line-height: 1.6; font-size: 1.1rem; margin: 0; font-weight: 500;">
            {question}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ✍️ Upload Your Handwritten Answer")
    st.markdown("📸 **Instructions:** Write your answer clearly on paper and take a high-quality photo.")
    
    # File uploader for answer image
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear image of your handwritten answer"
    )
    
    if uploaded_file is not None:
        # Display image
        from PIL import Image
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(image, caption="Answer Preview", use_container_width=True)
        
        with col2:
            st.markdown("### 🤖 **AI Evaluation**")
            
            if st.button("🔍 Evaluate My Answer", type="primary", use_container_width=True, key="evaluate_writing_answer"):
                # Store the evaluation trigger to display results below
                st.session_state.show_evaluation_results = True
                st.session_state.evaluation_image = image
                st.session_state.evaluation_question = question
                st.session_state.evaluation_marks = marks
                st.rerun()
        
        # Display evaluation results in full width below if triggered
        if st.session_state.get('show_evaluation_results', False):
            st.markdown("---")
            evaluate_writing_answer(
                st.session_state.evaluation_image, 
                st.session_state.evaluation_question, 
                st.session_state.evaluation_marks
            )
            # Clear the trigger after showing results
            st.session_state.show_evaluation_results = False
    
    # Control buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Generate New Question", key="generate_new_writing_question"):
            st.session_state.writing_quiz_active = False
            st.session_state.writing_quiz_question = None
            st.rerun()
    
    with col2:
        if st.button("📊 View Past Evaluations", key="view_writing_evaluations"):
            show_writing_quiz_history()
    
    with col3:
        if st.button("🏠 Back to Learning Hub", key="back_to_hub_writing_quiz"):
            st.session_state.writing_quiz_active = False
            st.session_state.writing_quiz_question = None
            st.rerun()

def evaluate_writing_answer(image, question, marks):
    """Evaluate the writing answer using OCR"""
    
    with st.spinner("🔍 Analyzing your handwritten answer..."):
        try:
            # Use OCR assistant
            if OCR_AVAILABLE:
                assistant = ExamAssistant(st.session_state.api_key)
            else:
                assistant = None
            if not assistant:
                st.error("❌ OCR functionality not available. Please ensure OCRapp.py is in the same directory.")
                return
            
            # Evaluate the handwritten answer
            evaluation = assistant.evaluate_handwritten_answer(
                image=image,
                topic=st.session_state.selected_topic,
                marks=marks,
                question=question
            )
            
            if evaluation:
                display_writing_evaluation(evaluation, marks)
                
                # Store evaluation in session
                if 'writing_quiz_evaluations' not in st.session_state:
                    st.session_state.writing_quiz_evaluations = []
                
                st.session_state.writing_quiz_evaluations.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'topic': st.session_state.selected_topic,
                    'subject': st.session_state.selected_subject,
                    'class': st.session_state.selected_class,
                    'question': question,
                    'marks': marks,
                    'evaluation': evaluation
                })
            else:
                st.error("❌ Could not evaluate answer. Please try again.")
                
        except Exception as e:
            st.error(f"⚠️ Error evaluating answer: {str(e)}")

def display_writing_evaluation(evaluation, total_marks):
    """Display the writing evaluation results"""
    
    st.markdown("### 📊 **Evaluation Results**")
    
    # Marks display
    marks_awarded = evaluation.get('marks_awarded', 0)
    percentage = (marks_awarded / total_marks) * 100 if total_marks > 0 else 0
    
    st.markdown(f"""
    <div style="
        font-size: 1.75rem;
        font-weight: bold;
        color: #1a237e;
        text-align: center;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        border: 2px solid #1a237e;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    ">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem; color: #1a237e;">
            {marks_awarded} / {total_marks}
        </div>
        <div style="font-size: 1.25rem; color: #495057; font-weight: 600;">
            {percentage:.1f}%
        </div>
        <div style="margin-top: 1rem; height: 8px; background-color: #e9ecef; border-radius: 4px;">
            <div style="width: {percentage}%; height: 100%; background-color: {
                '#1b5e20' if percentage >= 80 else
                '#2e7d32' if percentage >= 70 else
                '#f57c00' if percentage >= 60 else
                '#d32f2f'
            }; border-radius: 4px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Performance grade
    grade = (
        'Excellent' if percentage >= 80 else
        'Good' if percentage >= 70 else
        'Satisfactory' if percentage >= 60 else
        'Needs Improvement'
    )
    
    st.markdown(f"""
    <div style="text-align: center; margin-top: 0.5rem; color: {
        '#1b5e20' if percentage >= 80 else
        '#2e7d32' if percentage >= 70 else
        '#f57c00' if percentage >= 60 else
        '#d32f2f'
    };">
        <strong>{grade}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed evaluation sections
    col1, col2 = st.columns(2)
    
    with col1:
        if evaluation.get('extracted_text'):
            with st.expander("📝 Extracted Text", expanded=True):
                st.write(f"*{evaluation['extracted_text']}*")
        
        if evaluation.get('evaluation'):
            with st.expander("🔍 Detailed Evaluation", expanded=True):
                st.write(evaluation['evaluation'])
        
        if evaluation.get('correct_answer'):
            with st.expander("✅ Correct Answer", expanded=True):
                st.success("**Model Answer:**")
                st.write(evaluation['correct_answer'])
    
    with col2:
        if evaluation.get('feedback'):
            with st.expander("💡 Feedback & Suggestions", expanded=True):
                st.write(evaluation['feedback'])
        
        # Strengths and improvements
        if evaluation.get('strengths'):
            st.success("**✅ Strengths:**")
            for strength in evaluation['strengths']:
                st.write(f"• {strength}")
        
        if evaluation.get('improvements'):
            st.info("**📈 Areas for Improvement:**")
            for improvement in evaluation['improvements']:
                st.write(f"• {improvement}")

def show_writing_quiz_history():
    """Show past writing quiz evaluations"""
    
    if not st.session_state.get('writing_quiz_evaluations', []):
        st.info("📝 No past evaluations found. Complete some writing quizzes to see your history!")
        return
    
    st.markdown("### 📊 **Writing Quiz History**")
    
    for i, eval_data in enumerate(reversed(st.session_state.writing_quiz_evaluations)):
        with st.expander(f"📝 {eval_data['timestamp']} - {eval_data['topic']} ({eval_data['marks']} marks)", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Question:** {eval_data['question']}")
                st.write(f"**Subject:** {eval_data['subject']}")
                st.write(f"**Class:** {eval_data['class']}")
            
            with col2:
                evaluation = eval_data['evaluation']
                marks_awarded = evaluation.get('marks_awarded', 0)
                percentage = (marks_awarded / eval_data['marks']) * 100
                
                st.metric("Score", f"{marks_awarded}/{eval_data['marks']}")
                st.metric("Percentage", f"{percentage:.1f}%")
            
            if evaluation.get('feedback'):
                st.write(f"**Feedback:** {evaluation['feedback']}")
            
            if evaluation.get('correct_answer'):
                with st.expander("✅ View Correct Answer"):
                    st.success("**Model Answer:**")
                    st.write(evaluation['correct_answer'])

def final_writing_quiz_section():
    """Final Writing Quiz section with 3 questions of progressive difficulty - no intermediate feedback"""
    st.markdown("**Complete 3 writing questions with progressive difficulty!** Answer all questions sequentially, then get comprehensive feedback for all at the end.")
    
    # Show progressive difficulty structure
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Q1: 2 marks**\nFoundational")
    with col2:
        st.info("**Q2: 4 marks**\nIntermediate")
    with col3:
        st.info("**Q3: 8 marks**\nAdvanced")
    
    # Important notice about the exam flow
    st.warning("📋 **Exam Format:** You'll answer questions one by one. Feedback and scores will be shown only after completing all 3 questions!")
    
    # Check if OCR functionality is available
    if not OCR_AVAILABLE:
        st.error("❌ OCR functionality not available. Please ensure OCRapp.py is in the same directory.")
        return
    
    # Check if user has selected a topic
    if not st.session_state.selected_topic:
        st.warning("⚠️ Please select a topic first from the Learning Hub to generate writing questions.")
        return
    
    # Display current topic
    st.info(f"📚 **Current Topic:** {st.session_state.selected_topic}")
    st.info(f"📖 **Subject:** {st.session_state.selected_subject} | **Class:** {st.session_state.selected_class}")
    
    if not st.session_state.final_writing_quiz_active:
        # Quiz start section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📝 **Final Writing Quiz**")
            st.markdown("""
            **Exam Format:**
            - 3 comprehensive writing questions with progressive difficulty
            - Question 1: 2 marks (Foundational)
            - Question 2: 4 marks (Intermediate) 
            - Question 3: 8 marks (Advanced)
            - Answer questions sequentially (one at a time)
            - **No intermediate feedback during the exam**
            - Complete evaluation and feedback shown after all 3 questions
            """)
            
            if st.button("🚀 Start Final Writing Quiz", type="primary", use_container_width=True, key="start_final_writing_quiz"):
                st.session_state.final_writing_quiz_active = True
                st.session_state.final_writing_quiz_current_index = 0
                st.session_state.final_writing_quiz_questions = []
                st.session_state.final_writing_quiz_answers = {}
                st.session_state.final_writing_quiz_submitted = False
                st.session_state.final_writing_quiz_evaluations = {}
                st.session_state.final_writing_quiz_evaluation_in_progress = set()
                st.session_state.final_writing_quiz_evaluation_started = False
                st.rerun()
        
        with col2:
            st.markdown("### 💡 **Exam Instructions**")
            st.markdown("""
            ✅ Complete questions in order (Q1 → Q2 → Q3)  
            ✅ Progressive difficulty: 2→4→8 marks
            ✅ Write clearly on paper  
            ✅ Take high-quality photos  
            ✅ Submit one answer at a time  
            ✅ **No scores shown until the end**
            ✅ Complete feedback after final submission  
            """)
    
    elif not st.session_state.final_writing_quiz_submitted:
        # Active quiz
        conduct_final_writing_quiz()
    
    else:
        # Show results
        display_final_writing_results()

def conduct_final_writing_quiz():
    """Conduct the final writing quiz with 3 questions - no intermediate feedback"""
    
    current_index = st.session_state.final_writing_quiz_current_index
    total_questions = 3
    
    # Progressive marks display
    marks_progression = [2, 4, 8]
    current_marks = marks_progression[current_index] if current_index < len(marks_progression) else 2
    
    # Progress indicator with marks info
    st.markdown(f"### 📝 **Question {current_index + 1} of {total_questions}** ({current_marks} marks)")
    
    # Progress bar - show completed questions only
    progress = (current_index) / total_questions
    st.progress(progress, text=f"Progress: {current_index}/{total_questions} questions completed")
    
    # Check if we need to generate the current question
    if len(st.session_state.final_writing_quiz_questions) <= current_index:
        # Show generate button for first question, auto-generate for others
        if current_index == 0:
            if st.button("🎯 Generate 2 Mark Question", type="primary", use_container_width=True, key="generate_first_question"):
                generate_final_writing_question()
                st.rerun()
            return
        else:
            # Auto-generate subsequent questions
            generate_final_writing_question()
            st.rerun()
            return
    
    # Display current question if available
    if len(st.session_state.final_writing_quiz_questions) > current_index:
        question = st.session_state.final_writing_quiz_questions[current_index]
        
        # Display question in a styled box with correct marks
        st.markdown(f"""
        <div style="
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #1a237e;
            border: 1px solid #dee2e6;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        ">
            <h4 style="color: #1a237e; margin-bottom: 1rem; font-weight: bold;">Question {current_index + 1} ({current_marks} marks):</h4>
            <p style="color: #212529; line-height: 1.6; font-size: 1.1rem; margin: 0; font-weight: 500;">
                {question}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ✍️ Upload Your Handwritten Answer")
        st.markdown("📸 **Instructions:** Write your answer clearly on paper and take a high-quality photo.")
        
        # File uploader for answer image
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a clear image of your handwritten answer",
            key=f"final_writing_upload_{current_index}"
        )
        
        if uploaded_file is not None:
            # Display image
            from PIL import Image
            image = Image.open(uploaded_file)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(image, caption="Answer Preview", use_container_width=True)
            
            with col2:
                st.markdown("### 🤖 **Submit Answer**")
                
                # Different button text for final question
                if current_index == total_questions - 1:
                    button_text = "🏁 Submit Final Answer & Get Results"
                    success_text = "🎉 All answers submitted! Evaluating all responses..."
                else:
                    button_text = f"✅ Submit Answer {current_index + 1}"
                    success_text = f"✅ Answer {current_index + 1} submitted! Moving to next question..."
                
                if st.button(button_text, type="primary", use_container_width=True, key=f"submit_final_writing_{current_index}"):
                    # Store the answer
                    st.session_state.final_writing_quiz_answers[current_index] = {
                        'image': image,
                        'question': question,
                        'marks': current_marks,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Handle submission based on question number
                    if current_index < total_questions - 1:
                        # Moving to next question - start background evaluation for current question
                        # Q1->Q2: Start evaluating Q1 in background
                        # Q2->Q3: Start evaluating Q2 in background
                        trigger_background_evaluation(current_index)
                        
                        st.session_state.final_writing_quiz_current_index += 1
                        st.success(success_text)
                        st.rerun()
                    else:
                        # Final question submitted - evaluate all remaining questions
                        st.success(success_text)
                        
                        # Start evaluation for the final question (Q3)
                        trigger_background_evaluation(current_index)
                        
                        # Ensure all previous questions are evaluated if not already
                        for i in range(current_index):
                            if (i not in st.session_state.final_writing_quiz_evaluations and 
                                i not in st.session_state.final_writing_quiz_evaluation_in_progress):
                                trigger_background_evaluation(i)
                        
                        st.session_state.final_writing_quiz_submitted = True
                        st.info("⏳ Please wait while we evaluate all your answers...")
                        st.rerun()

    # Control buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Restart Quiz", key="restart_final_writing_quiz"):
            st.session_state.final_writing_quiz_active = False
            st.session_state.final_writing_quiz_current_index = 0
            st.session_state.final_writing_quiz_questions = []
            st.session_state.final_writing_quiz_answers = {}
            st.session_state.final_writing_quiz_submitted = False
            st.session_state.final_writing_quiz_evaluations = {}
            st.session_state.final_writing_quiz_evaluation_in_progress = set()
            st.rerun()
    
    with col2:
        if st.button("🏠 Back to Learning Hub", key="back_to_hub_final_writing_quiz"):
            st.session_state.final_writing_quiz_active = False
            st.rerun()

def trigger_background_evaluation(question_index: int):
    """Trigger background evaluation for a specific question"""
    
    # Check if evaluation is already in progress or completed
    if (question_index in st.session_state.final_writing_quiz_evaluation_in_progress or
        question_index in st.session_state.final_writing_quiz_evaluations):
        return
    
    # Check if answer exists
    if question_index not in st.session_state.final_writing_quiz_answers:
        return
    
    try:
        # Mark as in progress
        st.session_state.final_writing_quiz_evaluation_in_progress.add(question_index)
        
        # Initialize evaluation start times if not exists
        if not hasattr(st.session_state, 'evaluation_start_times'):
            st.session_state.evaluation_start_times = {}
        st.session_state.evaluation_start_times[question_index] = datetime.now()
        
        # Get answer data
        answer_data = st.session_state.final_writing_quiz_answers[question_index]
        
        # Perform evaluation
        if OCR_AVAILABLE:
            assistant = ExamAssistant(st.session_state.api_key)
            evaluation = assistant.evaluate_handwritten_answer(
                image=answer_data['image'],
                topic=st.session_state.selected_topic,
                marks=answer_data['marks'],
                question=answer_data['question']
            )
            
            if evaluation:
                # Store successful evaluation
                st.session_state.final_writing_quiz_evaluations[question_index] = {
                    'evaluation': evaluation,
                    'question': answer_data['question'],
                    'marks': answer_data['marks'],
                    'evaluated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                # Store error state
                st.session_state.final_writing_quiz_evaluations[question_index] = {
                    'error': 'Failed to evaluate answer - please try again',
                    'question': answer_data['question'],
                    'marks': answer_data['marks'],
                    'evaluated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        else:
            # Store OCR unavailable error
            st.session_state.final_writing_quiz_evaluations[question_index] = {
                'error': 'OCR functionality not available',
                'question': answer_data['question'],
                'marks': answer_data['marks'],
                'evaluated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    except Exception as e:
        # Store exception error
        st.session_state.final_writing_quiz_evaluations[question_index] = {
            'error': f'Evaluation error: {str(e)}',
            'question': answer_data['question'] if question_index in st.session_state.final_writing_quiz_answers else 'Unknown',
            'marks': answer_data['marks'] if question_index in st.session_state.final_writing_quiz_answers else 0,
            'evaluated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    finally:
        # Always clear in-progress state
        if question_index in st.session_state.final_writing_quiz_evaluation_in_progress:
            st.session_state.final_writing_quiz_evaluation_in_progress.remove(question_index)

def generate_final_writing_question():
    """Generate a writing question with progressive difficulty for the final writing quiz"""
    
    current_index = st.session_state.final_writing_quiz_current_index
    
    # Progressive marks: Q1=2, Q2=4, Q3=8
    marks_progression = [2, 4, 8]
    marks = marks_progression[current_index] if current_index < len(marks_progression) else 2
    
    # Progressive difficulty levels
    difficulty_progression = ["basic", "intermediate", "advanced"]
    difficulty = difficulty_progression[current_index] if current_index < len(difficulty_progression) else "basic"
    
    with st.spinner(f"🎯 Generating {marks}-mark question (Question {current_index + 1}/3)..."):
        try:
            # Use OCR assistant
            if OCR_AVAILABLE:
                assistant = ExamAssistant(st.session_state.api_key)
                
                if not assistant:
                    st.error("⚠️ Failed to initialize OCR assistant.")
                    # Provide fallback question
                    fallback_question = f"Write a detailed answer about {st.session_state.selected_topic}. Explain the key concepts and provide examples where applicable. ({marks} marks)"
                    st.session_state.final_writing_quiz_questions.append(fallback_question)
                    st.warning(f"🔄 Using fallback question for Question {current_index + 1}")
                    return
                    
                # Check API key
                if not st.session_state.api_key:
                    st.error("⚠️ API key not found. Please check your authentication.")
                    # Provide fallback question
                    fallback_question = f"Write a comprehensive answer about {st.session_state.selected_topic}. Cover the main points and explain with examples. ({marks} marks)"
                    st.session_state.final_writing_quiz_questions.append(fallback_question)
                    st.warning(f"🔄 Using fallback question for Question {current_index + 1}")
                    return
                
                # Generate question based on selected topic with progressive marks
                question = assistant.generate_question(
                    topic=st.session_state.selected_topic,
                    marks=marks
                )
                
                if question and question.strip():
                    st.session_state.final_writing_quiz_questions.append(question)
                    st.success(f"✅ Generated {marks}-mark question (Question {current_index + 1}/3)")
                else:
                    # Provide a fallback question
                    if marks == 2:
                        fallback_question = f"Briefly explain what {st.session_state.selected_topic} is and why it is important. (2 marks)"
                    elif marks == 4:
                        fallback_question = f"Explain {st.session_state.selected_topic} in detail with examples and its key features. (4 marks)"
                    else:  # 8 marks
                        fallback_question = f"Write a comprehensive essay about {st.session_state.selected_topic}. Include definitions, explanations, examples, advantages, disadvantages, and real-world applications. (8 marks)"
                    
                    st.session_state.final_writing_quiz_questions.append(fallback_question)
                    st.warning(f"🔄 Using fallback question for Question {current_index + 1}")
            else:
                st.error("⚠️ OCR functionality not available. Please ensure OCRapp.py is in the same directory.")
                # Provide a fallback question even when OCR is not available
                if marks == 2:
                    fallback_question = f"Briefly explain what {st.session_state.selected_topic} is and why it is important. (2 marks)"
                elif marks == 4:
                    fallback_question = f"Explain {st.session_state.selected_topic} in detail with examples and its key features. (4 marks)"
                else:  # 8 marks
                    fallback_question = f"Write a comprehensive essay about {st.session_state.selected_topic}. Include definitions, explanations, examples, advantages, disadvantages, and real-world applications. (8 marks)"
                
                st.session_state.final_writing_quiz_questions.append(fallback_question)
                st.warning(f"🔄 Using fallback question due to OCR unavailability (Question {current_index + 1})")
                
        except Exception as e:
            st.error(f"⚠️ Error generating question: {str(e)}")
            # Provide a fallback question in case of any error
            if marks == 2:
                fallback_question = f"Briefly explain what {st.session_state.selected_topic} is and why it is important. (2 marks)"
            elif marks == 4:
                fallback_question = f"Explain {st.session_state.selected_topic} in detail with examples and its key features. (4 marks)"
            else:  # 8 marks
                fallback_question = f"Write a comprehensive essay about {st.session_state.selected_topic}. Include definitions, explanations, examples, advantages, disadvantages, and real-world applications. (8 marks)"
            
            st.session_state.final_writing_quiz_questions.append(fallback_question)
            st.warning(f"🔄 Using fallback question due to error (Question {current_index + 1})")

def display_final_writing_results():
    """Display final writing quiz results - only after all evaluations are complete"""
    
    st.title("🏆 Final Writing Quiz Results")
    st.markdown("---")
    
    answers = st.session_state.final_writing_quiz_answers
    evaluations = st.session_state.final_writing_quiz_evaluations
    evaluation_in_progress = st.session_state.final_writing_quiz_evaluation_in_progress
    total_questions = len(answers)
    
    if total_questions == 0:
        st.warning("No answers found. Please complete the quiz first.")
        if st.button("🔙 Return to Quiz", key="return_to_quiz_from_results"):
            st.session_state.final_writing_quiz_active = True
            st.session_state.final_writing_quiz_submitted = False
            st.rerun()
        return
    
    # Check for any missing evaluations and trigger them automatically
    missing_evaluations = []
    for i in range(total_questions):
        if (i not in evaluations and 
            i not in evaluation_in_progress and 
            i in answers):
            missing_evaluations.append(i)
            # Trigger evaluation for missing questions
            trigger_background_evaluation(i)
    
    if missing_evaluations:
        st.info(f"🔄 Starting evaluations for questions: {[i+1 for i in missing_evaluations]}")
    
    # Header with quiz information
    st.info(f"📚 **Topic:** {st.session_state.selected_topic} | **Subject:** {st.session_state.selected_subject} | **Class:** {st.session_state.selected_class}")
    
    # Check if all evaluations are complete
    completed_evaluations = len([i for i in range(total_questions) if i in evaluations])
    all_evaluations_complete = completed_evaluations == total_questions
    
    if not all_evaluations_complete:
        # Show simple waiting message - no progress indicators
        st.markdown("### ⏳ **Evaluating Your Answers**")
        st.markdown("**Please wait while our AI evaluates all your responses...**")
        st.markdown(f"**Progress:** {completed_evaluations}/{total_questions} questions evaluated")
        
        # Simple refresh button
        if st.button("🔄 Check Results", key="check_results_simple"):
            st.rerun()
        
        # Auto-refresh every 3 seconds
        import time
        time.sleep(3)
        st.rerun()
        return
    
    # All evaluations complete - show complete results
    st.success("🎉 **All Evaluations Complete!** Here are your detailed results:")
    st.balloons()
    
    # Calculate total marks and scores
    total_possible_marks = sum([2, 4, 8])  # Progressive marks
    total_awarded_marks = 0
    
    for i in range(total_questions):
        if i in evaluations and evaluations[i].get('evaluation'):
            total_awarded_marks += evaluations[i]['evaluation'].get('marks_awarded', 0)
    
    overall_percentage = (total_awarded_marks / total_possible_marks) * 100 if total_possible_marks > 0 else 0
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Questions Completed", f"{total_questions}/3")
    
    with col2:
        st.metric("Total Score", f"{total_awarded_marks}/{total_possible_marks} marks")
    
    with col3:
        st.metric("Overall Percentage", f"{overall_percentage:.1f}%")
    
    # Overall performance indicator
    if overall_percentage >= 80:
        st.success("🎉 **Excellent Performance!** Outstanding writing skills demonstrated!")
    elif overall_percentage >= 70:
        st.success("👏 **Good Performance!** Strong writing abilities shown!")
    elif overall_percentage >= 60:
        st.warning("📚 **Fair Performance.** Room for improvement in writing skills.")
    else:
        st.error("📖 **Needs Improvement.** Focus on developing writing techniques.")
    
    st.markdown("---")
    
    # Display detailed results for each question
    st.markdown("### 📝 **Detailed Question-wise Results**")
    
    for i in range(total_questions):
        if i in answers:
            answer_data = answers[i]
            evaluation_data = evaluations.get(i)
            
            # Question header with marks
            marks_progression = [2, 4, 8]
            question_marks = marks_progression[i] if i < len(marks_progression) else 2
            
            with st.expander(f"� Question {i + 1} ({question_marks} marks)", expanded=True):
                # Question and answer display
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Question:** {answer_data['question']}")
                    st.markdown(f"**Submitted at:** {answer_data['timestamp']}")
                    
                    # Show evaluation results
                    if evaluation_data and evaluation_data.get('evaluation'):
                        evaluation = evaluation_data['evaluation']
                        marks_awarded = evaluation.get('marks_awarded', 0)
                        percentage = (marks_awarded / question_marks) * 100
                        
                        # Score display
                        st.markdown("---")
                        st.markdown("#### 📊 **Evaluation Results**")
                        
                        # Score with color coding
                        score_color = (
                            '#1b5e20' if percentage >= 80 else
                            '#2e7d32' if percentage >= 70 else
                            '#f57c00' if percentage >= 60 else
                            '#d32f2f'
                        )
                        
                        st.markdown(f"""
                        <div style="
                            background-color: #f8f9fa;
                            padding: 1rem;
                            border-radius: 8px;
                            border-left: 4px solid {score_color};
                            margin: 10px 0;
                        ">
                            <h3 style="color: {score_color}; margin: 0;">
                                {marks_awarded} / {question_marks} marks ({percentage:.1f}%)
                            </h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Detailed feedback
                        if evaluation.get('evaluation'):
                            st.markdown("**📝 Detailed Evaluation:**")
                            st.write(evaluation['evaluation'])
                        
                        if evaluation.get('correct_answer'):
                            st.markdown("**✅ Correct Answer:**")
                            st.success(evaluation['correct_answer'])
                        
                        if evaluation.get('feedback'):
                            st.markdown("**💡 Feedback:**")
                            st.write(evaluation['feedback'])
                        
                        if evaluation.get('extracted_text'):
                            with st.expander("📄 Extracted Text"):
                                st.write(f"*{evaluation['extracted_text']}*")
                    
                    else:
                        st.error("⚠️ **Evaluation failed or incomplete.**")
                
                with col2:
                    # Show image
                    st.image(answer_data['image'], caption=f"Answer {i + 1}", use_container_width=True)
    
    # Performance insights
    st.markdown("---")
    st.markdown("### 📈 **Performance Summary**")
    
    # Individual question performance
    question_scores = []
    for i in range(total_questions):
        marks_progression = [2, 4, 8]
        question_marks = marks_progression[i] if i < len(marks_progression) else 2
        if i in evaluations and evaluations[i].get('evaluation'):
            awarded = evaluations[i]['evaluation'].get('marks_awarded', 0)
            percentage = (awarded / question_marks) * 100
            question_scores.append(f"**Q{i + 1} ({question_marks} marks):** {awarded}/{question_marks} ({percentage:.1f}%)")
        else:
            question_scores.append(f"**Q{i + 1} ({question_marks} marks):** Evaluation failed")
    
    st.info(f"""
    🎯 **Individual Question Performance:**
    {chr(10).join(question_scores)}
    
    **Overall Achievement:** {total_awarded_marks}/{total_possible_marks} marks ({overall_percentage:.1f}%)
    """)
    
    # Action buttons
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Retake Writing Quiz", key="retake_final_writing_quiz_old"):
            st.session_state.final_writing_quiz_active = False
            st.session_state.final_writing_quiz_current_index = 0
            st.session_state.final_writing_quiz_questions = []
            st.session_state.final_writing_quiz_answers = {}
            st.session_state.final_writing_quiz_submitted = False
            st.session_state.final_writing_quiz_evaluations = {}
            st.session_state.final_writing_quiz_evaluation_in_progress = set()
            st.rerun()
    
    with col2:
        if st.button("✍️ Practice Individual Questions", key="practice_individual_writing_old"):
            st.info("💡 Go to Mini Quiz → Writing Quiz tab for individual question practice with evaluation!")
    
    with col3:
        if st.button("🏠 Back to Learning Hub", key="back_to_hub_final_writing_results_old"):
            st.session_state.final_writing_quiz_active = False
            st.rerun()

def final_quiz_section():
    """Final quiz section with two tabs - Multiple Choice and Writing Quiz"""
    st.subheader("📝 Final Quiz")
    
    # Create tabs for different quiz types
    tab1, tab2 = st.tabs(["📝 Multiple Choice Quiz", "✍️ Final Writing Quiz"])
    
    with tab1:
        final_multiple_choice_quiz_section()
    
    with tab2:
        final_writing_quiz_section()

def final_multiple_choice_quiz_section():
    """Final comprehensive multiple choice quiz section"""
    st.markdown("Test your complete understanding with a 10-question comprehensive quiz!")
    
    # Initialize final quiz state
    if 'final_quiz_active' not in st.session_state:
        st.session_state.final_quiz_active = False
        st.session_state.final_quiz_questions = []
        st.session_state.final_quiz_answers = {}
        st.session_state.final_quiz_submitted = False
        st.session_state.final_quiz_score = 0
    
    if not st.session_state.final_quiz_active:
        # Quiz start section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 **Ready for the Final Challenge?**")
            st.markdown("""
            **What you'll get:**
            - 10 comprehensive questions
            - Mix of easy, medium, and hard difficulty
            - Covers all aspects of the topic
            - Detailed feedback and explanations
            - Performance analytics
            """)
            
            if st.button("🚀 Start Final Quiz", type="primary", use_container_width=True, key="start_final_quiz"):
                generate_final_quiz()
        
        with col2:
            # Show preparation tips
            st.markdown("### 💡 **Preparation Tips**")
            st.markdown("""
            ✅ Review topic explanation  
            ✅ Complete mini quiz practice  
            ✅ Watch educational videos  
            ✅ Aim for 70%+ score  
            ✅ Take your time to think  
            """)
    
    elif not st.session_state.final_quiz_submitted:
        # Active quiz
        conduct_final_quiz()
    
    else:
        # Show results
        display_final_quiz_results()

def generate_final_quiz():
    """Generate final quiz questions"""
    with st.spinner("🎯 Generating comprehensive final quiz..."):
        try:
            quiz_generator = QuizGenerator(st.session_state.api_key)
            
            questions = quiz_generator.generate_final_quiz(
                topic=st.session_state.selected_topic,
                subject=st.session_state.selected_subject,
                class_level=st.session_state.selected_class
            )
            
            if questions and len(questions) > 0:
                st.session_state.final_quiz_questions = questions
                st.session_state.final_quiz_active = True
                st.session_state.final_quiz_answers = {}
                st.session_state.final_quiz_submitted = False
                st.success("✅ Final quiz generated successfully!")
                st.rerun()
            else:
                st.error("❌ Could not generate quiz questions. Please try again.")
                
        except Exception as e:
            st.error(f"⚠️ Error generating final quiz: {str(e)}")

def conduct_final_quiz():
    """Display and conduct final quiz"""
    questions = st.session_state.final_quiz_questions
    
    st.markdown("### 📝 **Final Comprehensive Quiz**")
    st.markdown(f"**Topic:** {st.session_state.selected_topic}")
    st.markdown("**Instructions:** Answer all 10 questions and submit when ready.")
    
    st.markdown("---")
    
    # Display all questions
    for i, question in enumerate(questions):
        st.markdown(f"#### Question {i+1}")
        st.markdown(f"**{question['question']}**")
        
        # Answer options
        answer_key = f"final_q_{i}"
        selected_answer = st.radio(
            "Select your answer:",
            question['options'],
            key=answer_key,
            index=None
        )
        
        # Store answer
        if selected_answer:
            st.session_state.final_quiz_answers[i] = selected_answer
        
        st.markdown("---")
    
    # Submit button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        answered_count = len(st.session_state.final_quiz_answers)
        total_questions = len(questions)
        
        if answered_count == total_questions:
            if st.button("✅ Submit Final Quiz", type="primary", use_container_width=True, key="submit_final_quiz"):
                calculate_final_quiz_score()
        else:
            st.warning(f"⚠️ Please answer all questions ({answered_count}/{total_questions} completed)")
            st.button("✅ Submit Final Quiz", disabled=True, use_container_width=True, key="submit_final_quiz_disabled")

def calculate_final_quiz_score():
    """Calculate and store final quiz score"""
    questions = st.session_state.final_quiz_questions
    answers = st.session_state.final_quiz_answers
    
    correct_count = 0
    detailed_results = []
    
    for i, question in enumerate(questions):
        user_answer = answers.get(i, "")
        correct_answer = question['correct_answer']
        is_correct = user_answer == correct_answer
        
        if is_correct:
            correct_count += 1
        
        detailed_results.append({
            'question': question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': question.get('explanation', ''),
            'difficulty': question.get('difficulty', 'medium')
        })
    
    # Calculate score
    total_questions = len(questions)
    score_percentage = (correct_count / total_questions) * 100
    
    # Store results
    st.session_state.final_quiz_score = score_percentage
    st.session_state.final_quiz_detailed_results = detailed_results
    st.session_state.final_quiz_submitted = True
    
    # Record in history
    st.session_state.student_history.add_quiz_attempt(
        topic=st.session_state.selected_topic,
        quiz_type="Final Quiz",
        score=score_percentage,
        total_questions=total_questions,
        correct_answers=correct_count
    )
    
    st.rerun()

def display_final_quiz_results():
    """Display final quiz results and feedback"""
    score = st.session_state.final_quiz_score
    results = st.session_state.final_quiz_detailed_results
    
    st.markdown("### 🎊 **Final Quiz Results**")
    
    # Score display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Your Score", f"{score:.1f}%")
    
    with col2:
        correct_count = sum(1 for r in results if r['is_correct'])
        st.metric("Correct Answers", f"{correct_count}/{len(results)}")
    
    with col3:
        if score >= 80:
            grade = "Excellent! 🏆"
            color = "success"
        elif score >= 70:
            grade = "Good! 👍"
            color = "success"
        elif score >= 60:
            grade = "Fair 📚"
            color = "warning"
        else:
            grade = "Needs Improvement 📖"
            color = "error"
        
        if color == "success":
            st.success(grade)
        elif color == "warning":
            st.warning(grade)
        else:
            st.error(grade)
    
    # Performance feedback
    st.markdown("---")
    
    if score >= 80:
        st.success("🎉 **Outstanding Performance!** You have excellent mastery of this topic!")
    elif score >= 70:
        st.success("👏 **Good Job!** You have a solid understanding of this topic!")
    elif score >= 60:
        st.warning("📚 **Fair Performance.** Consider reviewing the topic and practicing more.")
    else:
        st.error("📖 **Needs Improvement.** Please review the topic materials and try the mini quiz for more practice.")
    
    # Detailed results
    st.markdown("### 📊 **Detailed Results**")
    
    for i, result in enumerate(results):
        with st.expander(f"Question {i+1} - {'✅ Correct' if result['is_correct'] else '❌ Incorrect'}"):
            st.markdown(f"**Question:** {result['question']}")
            st.markdown(f"**Your Answer:** {result['user_answer']}")
            st.markdown(f"**Correct Answer:** {result['correct_answer']}")
            
            if result['explanation']:
                st.markdown(f"**Explanation:** {result['explanation']}")
            
            st.markdown(f"**Difficulty:** {result['difficulty'].title()}")
    
    # Action buttons
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Retake Final Quiz", key="retake_final_quiz"):
            st.session_state.final_quiz_active = False
            st.session_state.final_quiz_submitted = False
            st.session_state.final_quiz_questions = []
            st.session_state.final_quiz_answers = {}
            st.rerun()
    
    with col2:
        if st.button("🧩 Practice More (Mini Quiz)", key="practice_more_mini_quiz"):
            # Switch to mini quiz
            st.session_state.final_quiz_active = False
            st.session_state.final_quiz_submitted = False
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Learning Hub", key="back_to_hub_final_quiz"):
            st.session_state.final_quiz_active = False
            st.session_state.final_quiz_submitted = False
            st.rerun()

def analyze_user_strengths_weaknesses(history, session_state):
    """Analyze user's learning patterns to identify realistic strengths and weaknesses"""
    
    strengths = []
    weaknesses = []
    recommendations = []
    
    # Analyze quiz performance
    quiz_attempts = history.quiz_attempts
    writing_evaluations = session_state.get('writing_quiz_evaluations', [])
    topics_studied = history.topics_studied
    chat_interactions = history.chat_interactions
    video_views = history.video_views
    
    # Calculate basic stats
    total_quizzes = len(quiz_attempts)
    total_topics = len(topics_studied)
    total_chats = len(chat_interactions)
    total_videos = len(video_views)
    total_writing_quizzes = len(writing_evaluations)
    
    # Initialize variables that might be used later
    avg_score = 0
    recent_avg = 0
    avg_writing_score = 0
    
    # Quiz Performance Analysis
    if total_quizzes > 0:
        avg_score = sum(q['score'] for q in quiz_attempts) / total_quizzes
        recent_scores = [q['score'] for q in quiz_attempts[-5:]] if len(quiz_attempts) >= 5 else [q['score'] for q in quiz_attempts]
        recent_avg = sum(recent_scores) / len(recent_scores)
        
        # Performance-based strengths and weaknesses
        if avg_score >= 80:
            strengths.append("Excellent quiz performance with strong conceptual understanding")
        elif avg_score >= 70:
            strengths.append("Good quiz performance showing solid grasp of concepts")
        elif avg_score >= 60:
            strengths.append("Steady quiz performance with room for improvement")
        else:
            weaknesses.append("Quiz scores indicate need for more concept review and practice")
        
        # Improvement trend analysis
        if len(quiz_attempts) >= 3:
            early_scores = [q['score'] for q in quiz_attempts[:3]]
            late_scores = [q['score'] for q in quiz_attempts[-3:]]
            early_avg = sum(early_scores) / len(early_scores)
            late_avg = sum(late_scores) / len(late_scores)
            improvement = late_avg - early_avg
            
            if improvement > 15:
                strengths.append("Showing excellent learning progression and improvement over time")
            elif improvement > 5:
                strengths.append("Demonstrating positive learning trends and skill development")
            elif improvement < -10:
                weaknesses.append("Performance decline suggests need for better study strategies")
    else:
        weaknesses.append("Limited quiz practice - take more quizzes to assess understanding")
    
    # Writing Quiz Analysis
    if total_writing_quizzes > 0:
        writing_scores = []
        for eval_data in writing_evaluations:
            evaluation = eval_data.get('evaluation', {})
            marks_awarded = evaluation.get('marks_awarded', 0)
            total_marks = eval_data.get('marks', 1)
            percentage = (marks_awarded / total_marks) * 100
            writing_scores.append(percentage)
        
        avg_writing_score = sum(writing_scores) / len(writing_scores)
        
        if avg_writing_score >= 75:
            strengths.append("Strong written communication and expression skills")
        elif avg_writing_score >= 60:
            strengths.append("Good writing abilities with clear expression of ideas")
        else:
            weaknesses.append("Written expression needs improvement - practice more writing exercises")
        
        # Analyze writing progression
        if len(writing_scores) >= 2:
            recent_writing_avg = sum(writing_scores[-2:]) / len(writing_scores[-2:])
            if recent_writing_avg > avg_writing_score:
                strengths.append("Improving writing skills through consistent practice")
    
    # Learning Engagement Analysis
    if total_topics >= 5:
        strengths.append("High engagement with diverse topics showing curiosity and dedication")
    elif total_topics >= 2:
        strengths.append("Good topic exploration showing interest in learning")
    else:
        weaknesses.append("Limited topic exploration - try studying more diverse subjects")
    
    # Interactive Learning Analysis
    if total_chats >= 10:
        strengths.append("Active learner who asks questions and seeks clarification")
    elif total_chats >= 5:
        strengths.append("Good use of Q&A feature for doubt resolution")
    elif total_chats < 2:
        weaknesses.append("Underutilizing Q&A feature - ask more questions to enhance understanding")
    
    # Video Learning Analysis
    if total_videos >= 5:
        strengths.append("Multi-modal learner effectively using visual learning resources")
    elif total_videos >= 2:
        strengths.append("Good use of video resources for enhanced understanding")
    else:
        weaknesses.append("Limited use of video learning - visual content can improve comprehension")
    
    # Topic-wise Performance Analysis
    if total_quizzes > 0:
        topic_performance = {}
        for quiz in quiz_attempts:
            topic = quiz.get('topic', 'Unknown')
            score = quiz.get('score', 0)
            if topic not in topic_performance:
                topic_performance[topic] = []
            topic_performance[topic].append(score)
        
        topic_averages = {topic: sum(scores)/len(scores) for topic, scores in topic_performance.items()}
        
        # Find strongest and weakest topics
        if topic_averages:
            best_topic = max(topic_averages.items(), key=lambda x: x[1])
            worst_topic = min(topic_averages.items(), key=lambda x: x[1])
            
            if best_topic[1] >= 70:
                strengths.append(f"Particular strength in '{best_topic[0]}' with {best_topic[1]:.1f}% average")
            
            if worst_topic[1] <= 60 and len(topic_averages) > 1:
                weaknesses.append(f"Needs improvement in '{worst_topic[0]}' (average: {worst_topic[1]:.1f}%)")
    
    # Learning Pattern Analysis
    if total_quizzes > 0 and total_topics > 0:
        quiz_to_topic_ratio = total_quizzes / total_topics
        if quiz_to_topic_ratio >= 2:
            strengths.append("Thorough learner who practices extensively on each topic")
        elif quiz_to_topic_ratio < 0.5:
            weaknesses.append("Tends to study topics without sufficient practice - take more quizzes per topic")
    
    # Generate Recommendations based on analysis
    if avg_score < 70 and total_quizzes > 0:
        recommendations.append("Focus on concept clarity before attempting quizzes")
        recommendations.append("Review incorrect answers and understand the reasoning")
    
    if total_writing_quizzes < 2:
        recommendations.append("Practice more writing quizzes to improve expression skills")
    
    if total_chats < 5:
        recommendations.append("Use the AI Assistant feature more to clarify doubts instantly")
    
    if total_videos < 3:
        recommendations.append("Watch educational videos for better visual understanding")
    
    if len(set(topic['topic'] for topic in topics_studied)) < 3:
        recommendations.append("Explore more diverse topics to broaden knowledge base")
    
    # Ensure we have some content even for new users
    if not strengths:
        strengths.append("Getting started with the learning journey - positive engagement observed")
    
    if not weaknesses:
        weaknesses.append("Continue current learning approach while exploring new features")
    
    if not recommendations:
        recommendations.append("Continue consistent practice and engagement with all learning features")
        recommendations.append("Set regular study schedules for optimal learning outcomes")
    
    # Generate overall assessment
    total_activities = total_quizzes + total_topics + total_chats + total_videos + total_writing_quizzes
    
    if total_activities >= 20:
        engagement_level = "highly engaged"
    elif total_activities >= 10:
        engagement_level = "moderately engaged"
    else:
        engagement_level = "starting to engage"
    
    if total_quizzes > 0:
        performance_descriptor = "excellent" if avg_score >= 80 else "good" if avg_score >= 70 else "developing"
        overall_assessment = f"You are a {engagement_level} learner with {performance_descriptor} academic performance. Your learning style shows {len(strengths)} key strengths and {len(weaknesses)} areas for growth."
    else:
        overall_assessment = f"You are a {engagement_level} learner who is building foundational knowledge. Focus on taking quizzes to assess your understanding and identify specific areas for improvement."
    
    return {
        'strengths': strengths,
        'weaknesses': weaknesses,
        'recommendations': recommendations,
        'overall_assessment': overall_assessment
    }

def progress_section():
    """Student progress tracking section"""
    st.subheader("📊 My Learning Progress")
    
    history = st.session_state.student_history
    
    # Overview stats
    st.markdown("### 📈 **Overview**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        topics_studied = len(history.topics_studied)
        st.metric("Topics Studied", topics_studied)
    
    with col2:
        quizzes_taken = len(history.quiz_attempts)
        st.metric("Quizzes Taken", quizzes_taken)
    
    with col3:
        videos_watched = len(history.video_views)
        st.metric("Videos Watched", videos_watched)
    
    with col4:
        if quizzes_taken > 0:
            avg_score = sum(q['score'] for q in history.quiz_attempts) / quizzes_taken
            st.metric("Average Score", f"{avg_score:.1f}%")
        else:
            st.metric("Average Score", "N/A")
    
    # AI-Powered Personalized Feedback Section
    st.markdown("---")
    st.markdown("### 🤖 **AI-Powered Learning Insights & Feedback**")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("""
        Get personalized feedback based on your learning patterns, mistakes, and progress. 
        Our AI analyzes your interactions, quiz performance, and study habits to provide tailored insights and recommendations.
        """)
    
    with col2:
        generate_feedback = st.button("🧠 Generate AI Feedback", type="primary", use_container_width=True, key="generate_ai_feedback")
    
    with col3:
        analyze_strengths_weaknesses = st.button("💪 Strengths & Weaknesses", type="secondary", use_container_width=True, key="analyze_strengths_weaknesses")
    
    # Display feedback outside of columns for better readability
    if generate_feedback:
        # Prepare comprehensive student data for analysis
        student_data = {
            'student_name': st.session_state.student_name,
            'class_level': st.session_state.get('selected_class', 'Unknown'),
            'current_subject': st.session_state.get('selected_subject', 'General'),
            'current_topic': st.session_state.get('selected_topic', 'General Learning'),
            'quiz_attempts': history.quiz_attempts,
            'topics_studied': history.topics_studied,
            'chat_interactions': history.chat_interactions,
            'video_views': history.video_views,
            'continuous_quiz_stats': st.session_state.get('continuous_quiz_stats', {}),
            'final_quiz_results': getattr(history, 'final_quiz_results', []),
            'writing_quiz_evaluations': st.session_state.get('writing_quiz_evaluations', [])
        }
        
        with st.spinner("🧠 Analyzing your learning patterns and generating personalized feedback..."):
            try:
                # Generate AI-powered feedback
                ai_assistant = AIAssistant(st.session_state.api_key)
                feedback = ai_assistant.generate_comprehensive_feedback(student_data)
                
                # Display the feedback in an attractive format with full width
                st.markdown("---")
                st.markdown("## 📋 **Your Personalized Learning Report**")
                st.markdown(feedback)
                
                # Add timestamp
                st.caption(f"📅 Report generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
                
            except Exception as e:
                st.error(f"❌ Error generating feedback: {str(e)}")
                
                # Provide basic fallback feedback
                st.markdown("---")
                st.markdown("## 📋 **Basic Learning Summary**")
                
                if quizzes_taken > 0:
                    if avg_score > 75:
                        st.success(f"🌟 Excellent work, {st.session_state.student_name}! Your average score of {avg_score:.1f}% shows strong understanding.")
                    elif avg_score > 60:
                        st.info(f"👍 Good progress, {st.session_state.student_name}! Your average score of {avg_score:.1f}% shows you're learning well.")
                    else:
                        st.warning(f"📚 Keep practicing, {st.session_state.student_name}! Your average score of {avg_score:.1f}% suggests reviewing key concepts would help.")
                
                st.markdown(f"""
                **📊 Your Learning Stats:**
                - Topics Explored: {topics_studied}
                - Quizzes Completed: {quizzes_taken}
                - Videos Watched: {videos_watched}
                - Questions Asked: {len(history.chat_interactions)}
                
                **💡 Quick Recommendations:**
                - Continue taking quizzes to test your knowledge
                - Use the interactive Q&A feature when you have questions
                - Watch educational videos for better understanding
                - Review topics where you scored below 70%
                """)
    
    # Strengths & Weaknesses Analysis
    if analyze_strengths_weaknesses:
        with st.spinner("🔍 Analyzing your learning patterns to identify strengths and weaknesses..."):
            try:
                # Prepare comprehensive data for analysis
                strengths_weaknesses_data = analyze_user_strengths_weaknesses(history, st.session_state)
                
                # Display the analysis in an attractive format
                st.markdown("---")
                st.markdown("## 💪 **Your Learning Strengths & Weaknesses Analysis**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### ✅ **Your Strengths**")
                    for strength in strengths_weaknesses_data['strengths']:
                        st.success(f"💪 {strength}")
                
                with col2:
                    st.markdown("### 🎯 **Areas for Improvement**")
                    for weakness in strengths_weaknesses_data['weaknesses']:
                        st.warning(f"📈 {weakness}")
                
                # Overall Assessment
                st.markdown("### 📊 **Overall Learning Assessment**")
                st.info(strengths_weaknesses_data['overall_assessment'])
                
                # Specific Recommendations
                st.markdown("### 💡 **Personalized Recommendations**")
                for recommendation in strengths_weaknesses_data['recommendations']:
                    st.markdown(f"• {recommendation}")
                
                # Add timestamp
                st.caption(f"📅 Analysis generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
                
            except Exception as e:
                st.error(f"❌ Error generating analysis: {str(e)}")
                st.info("💡 Complete more activities to get a comprehensive analysis of your strengths and weaknesses.")
    
    # Recent activity
    st.markdown("---")
    st.markdown("### 🕒 **Recent Activity**")
    
    if history.topics_studied:
        st.markdown("**Topics Studied:**")
        for topic_data in history.topics_studied[-5:]:  # Last 5 topics
            timestamp = topic_data['timestamp'].strftime("%Y-%m-%d %H:%M")
            st.markdown(f"• {topic_data['topic']} ({topic_data['subject']}) - {timestamp}")
    
    if history.quiz_attempts:
        st.markdown("**Recent Quiz Attempts:**")
        for quiz_data in history.quiz_attempts[-5:]:  # Last 5 quizzes
            timestamp = quiz_data['timestamp'].strftime("%Y-%m-%d %H:%M")
            st.markdown(f"• {quiz_data['topic']} - {quiz_data['score']:.1f}% - {timestamp}")
    
    # Detailed Performance Analytics
    st.markdown("---")
    st.markdown("### 📈 **Detailed Performance Analytics**")
    
    if history.quiz_attempts:
        # Performance over time chart
        quiz_dates = [q['timestamp'].strftime('%m/%d') for q in history.quiz_attempts[-10:]]
        quiz_scores = [q['score'] for q in history.quiz_attempts[-10:]]
        
        if len(quiz_scores) > 1:
            col1, col2 = st.columns(2)
            
            with col1:
                if PLOTLY_AVAILABLE:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=quiz_dates,
                        y=quiz_scores,
                        mode='lines+markers',
                        name='Quiz Scores',
                        line=dict(color='#ff6b6b', width=3),
                        marker=dict(size=8)
                    ))
                    fig.update_layout(
                        title="📊 Recent Quiz Performance Trend",
                        xaxis_title="Date",
                        yaxis_title="Score (%)",
                        yaxis=dict(range=[0, 100]),
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Fallback visualization using Streamlit's built-in chart
                    import pandas as pd
                    chart_data = pd.DataFrame({
                        'Date': quiz_dates,
                        'Score': quiz_scores
                    })
                    st.line_chart(chart_data.set_index('Date'))
                    st.caption("📊 Recent Quiz Performance Trend")
            
            with col2:
                # Subject-wise performance
                subject_performance = {}
                for quiz in history.quiz_attempts:
                    topic = quiz.get('topic', 'Unknown')
                    score = quiz.get('score', 0)
                    if topic not in subject_performance:
                        subject_performance[topic] = []
                    subject_performance[topic].append(score)
                
                if subject_performance:
                    avg_by_topic = {topic: sum(scores)/len(scores) for topic, scores in subject_performance.items()}
                    
                    if PLOTLY_AVAILABLE:
                        fig2 = go.Figure(data=[
                            go.Bar(
                                x=list(avg_by_topic.keys()),
                                y=list(avg_by_topic.values()),
                                marker_color=['#ff6b6b' if score < 60 else '#4ecdc4' if score < 80 else '#95e1d3' for score in avg_by_topic.values()]
                            )
                        ])
                        fig2.update_layout(
                            title="📋 Performance by Topic",
                            xaxis_title="Topics",
                            yaxis_title="Average Score (%)",
                            yaxis=dict(range=[0, 100]),
                            height=400
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                    else:
                        # Fallback visualization using Streamlit's built-in chart
                        import pandas as pd
                        chart_data = pd.DataFrame({
                            'Topic': list(avg_by_topic.keys()),
                            'Average Score': list(avg_by_topic.values())
                        })
                        st.bar_chart(chart_data.set_index('Topic'))
                        st.caption("📋 Performance by Topic")
        
        # Learning insights
        st.markdown("#### 🎯 **Quick Learning Insights**")
        
        recent_scores = [q['score'] for q in history.quiz_attempts[-5:]]
        early_scores = [q['score'] for q in history.quiz_attempts[:5]] if len(history.quiz_attempts) > 5 else []
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if recent_scores:
                recent_avg = sum(recent_scores) / len(recent_scores)
                if recent_avg > 80:
                    st.success(f"🌟 **Recent Performance**\nExcellent! {recent_avg:.1f}% average")
                elif recent_avg > 60:
                    st.info(f"👍 **Recent Performance**\nGood progress! {recent_avg:.1f}% average")
                else:
                    st.warning(f"📚 **Recent Performance**\nKeep practicing! {recent_avg:.1f}% average")
        
        with col2:
            if early_scores and recent_scores:
                early_avg = sum(early_scores) / len(early_scores)
                recent_avg = sum(recent_scores) / len(recent_scores)
                improvement = recent_avg - early_avg
                
                if improvement > 10:
                    st.success(f"📈 **Improvement**\nGreat progress! +{improvement:.1f}%")
                elif improvement > 0:
                    st.info(f"📊 **Improvement**\nSteady growth! +{improvement:.1f}%")
                else:
                    st.warning(f"📉 **Improvement**\nNeed focus! {improvement:.1f}%")
        
        with col3:
            total_questions = sum(q.get('total_questions', 0) for q in history.quiz_attempts)
            total_correct = sum(q.get('correct_answers', 0) for q in history.quiz_attempts)
            
            if total_questions > 0:
                accuracy = (total_correct / total_questions) * 100
                if accuracy > 75:
                    st.success(f"🎯 **Overall Accuracy**\nExcellent! {accuracy:.1f}%")
                elif accuracy > 60:
                    st.info(f"🎯 **Overall Accuracy**\nGood! {accuracy:.1f}%")
                else:
                    st.warning(f"🎯 **Overall Accuracy**\nImproving! {accuracy:.1f}%")
    
    # Export data buttons
    st.markdown("---")
    st.markdown("### 📥 **Export Learning Reports**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate PDF Report", type="primary", use_container_width=True, key="generate_pdf_report"):
            with st.spinner("📄 Generating PDF report..."):
                try:
                    pdf_data = history.generate_pdf_report(st.session_state.student_name)
                    
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_data,
                        file_name=f"learning_report_{st.session_state.student_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("✅ PDF report generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
    
    with col2:
        if st.button("📊 Export JSON Data", use_container_width=True, key="export_json_data"):
            export_data = {
                'student_name': st.session_state.student_name,
                'topics_studied': [
                    {
                        'topic': t['topic'],
                        'subject': t['subject'],
                        'chapter': t['chapter'],
                        'class': t['class'],
                        'timestamp': t['timestamp'].isoformat()
                    }
                    for t in history.topics_studied
                ],
                'quiz_attempts': [
                    {
                        'topic': q['topic'],
                        'quiz_type': q['quiz_type'],
                        'score': q['score'],
                        'total_questions': q['total_questions'],
                        'correct_answers': q['correct_answers'],
                        'timestamp': q['timestamp'].isoformat()
                    }
                    for q in history.quiz_attempts
                ],
                'video_views': [
                    {
                        'topic': v['topic'],
                        'video_title': v['video_title'],
                        'timestamp': v['timestamp'].isoformat()
                    }
                    for v in history.video_views
                ]
            }
            
            json_data = json.dumps(export_data, indent=2)
            st.download_button(
                label="📥 Download JSON Data",
                data=json_data,
                file_name=f"learning_data_{st.session_state.student_name}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )

def main():
    """Main application function"""
    
    # Initialize session state
    initialize_session_state()
    
    # Display appropriate page based on current state
    if st.session_state.current_page == "authentication":
        authentication_page()
    elif st.session_state.current_page == "preferences_survey":
        preferences_survey_page()
    elif st.session_state.current_page == "class_selection":
        class_selection_page()
    elif st.session_state.current_page == "subject_selection":
        subject_selection_page()
    elif st.session_state.current_page == "chapter_selection":
        chapter_selection_page()
    elif st.session_state.current_page == "topic_selection":
        topic_selection_page()
    elif st.session_state.current_page == "learning_hub":
        learning_hub_page()

if __name__ == "__main__":
    main()