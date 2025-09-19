# Still Working on This Project...
### With love for AP students ❤️

## 🎓 AI-Powered Student Learning App For AP STATE Students

An intelligent learning platform designed specifically for AP State Board Syllabus (Classes 1-10) using advanced AI technology.

## 🚀 Features

### 🔐 **Authentication**
- Secure OpenAI API key integration
- Student profile management

### 📚 **Structured Learning Flow**
1. **Class Selection** - Choose your grade level (1-10)
2. **Subject Selection** - Pick from curriculum subjects
3. **Chapter Selection** - Navigate through organized chapters
4. **Topic Selection** - Focus on specific learning topics

### 🎯 **Core Learning Features**

#### 📖 **Topic Explanation**
- AI-generated, age-appropriate explanations
- Structured content with real-world examples
- Grade-level optimized language

#### 💬 **Interactive Q&A Chat**
- Real-time AI assistance for topic-related questions
- Contextual responses based on current learning
- Encourages curiosity and deeper understanding

#### 🎥 **Video Learning**
- Curated educational YouTube videos
- Filtered content from trusted educational channels
- Relevance-based video ranking

### 🧩 **Assessment Features**

#### **Mini Quiz (Adaptive)**
- Starts with easy questions
- Dynamically adjusts difficulty based on performance
- Progressive difficulty: Easy → Medium → Hard
- Immediate feedback and explanations

#### **Final Quiz**
- Comprehensive 10-question assessment
- Mixed difficulty levels
- Detailed performance analysis
- Downloadable results

### 📊 **Progress Tracking**

#### **Student History**
- Complete learning journey tracking
- Quiz performance analytics
- Study streak monitoring
- Weak area identification

#### **Progress Reports**
- Downloadable detailed reports
- Strengths and weaknesses analysis
- Personalized study recommendations
- Performance trends

## 🛠️ **Technology Stack**

- **Frontend**: Streamlit
- **AI/LLM**: OpenAI GPT-4o mini via LangChain
- **Video Search**: YouTube Search Python
- **Data Processing**: Python, JSON
- **State Management**: Streamlit Session State

## 📋 **Installation**

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- OpenAI API Key
- Internet connection for video recommendations

### Setup Steps

1. **Clone or download the project files**
2. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**:
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** and navigate to the displayed URL (usually `http://localhost:8501`)

## 🔑 **Getting OpenAI API Key**

1. Go to [OpenAI API](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Create a new API key
4. Copy the key (starts with `sk-`)
5. Enter the key in the app's authentication page

## 📖 **How to Use**

### First Time Setup
1. Enter your name and OpenAI API key
2. Click "Start Learning Journey"

### Learning Flow
1. **Select Class** - Choose your grade level
2. **Choose Subject** - Pick Mathematics, Science, or Environmental Studies
3. **Select Chapter** - Navigate to your desired chapter
4. **Pick Topic** - Choose the specific topic to learn

### Learning Modes
- **📖 Topic Explanation** - Get AI-generated explanations
- **💬 Interactive Q&A** - Ask questions and get instant answers
- **🎥 Video Learning** - Watch curated educational videos
- **🧩 Mini Quiz** - Take adaptive difficulty quizzes
- **📝 Final Quiz** - Complete comprehensive assessments
- **📊 My Progress** - View your learning analytics

## 📚 **Curriculum Coverage**

The app covers the complete AP State Board syllabus for:

### Classes 1-2
- Basic Mathematics (Numbers, Shapes, Patterns)
- Environmental Studies (Self, Family, Surroundings)

### Classes 3-5
- Advanced Mathematics (Operations, Geometry, Measurement)
- Environmental Studies (Resources, Health, Human Body)

### Classes 6-8
- Mathematics (Algebra, Geometry, Mensuration)
- Science (Physics, Chemistry, Biology concepts)

### Classes 9-10 (SSC)
- Mathematics (Advanced topics, Statistics, Probability)
- Physical Science (Physics and Chemistry)
- Biology (Life Processes, Genetics)

## 🎯 **Key Benefits**

### For Students
- **Personalized Learning** - AI adapts to individual pace
- **Comprehensive Coverage** - Complete AP State Board syllabus
- **Multiple Learning Modes** - Visual, auditory, and interactive
- **Progress Tracking** - Monitor improvement over time
- **Instant Help** - 24/7 AI assistance

### For Educators
- **Student Analytics** - Detailed progress reports
- **Curriculum Alignment** - Follows official AP State Board syllabus
- **Assessment Tools** - Automated quiz generation and grading

## 🔧 **Project Structure**

```
project/
├── app.py                 # Main Streamlit application
├── curriculum_data.py     # AP State Board syllabus data
├── ai_assistant.py        # AI-powered content generation
├── quiz_generator.py      # Adaptive and final quiz creation
├── video_recommender.py   # Educational video discovery
├── student_history.py     # Progress tracking and analytics
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🛡️ **Privacy & Security**

- **API Key Security** - Keys are stored only in session state
- **No Data Storage** - Student data is not permanently stored
- **Local Processing** - All data processing happens locally
- **Privacy First** - No personal information is shared externally

## 🚨 **Troubleshooting**

### Common Issues

1. **API Key Error**
   - Ensure your OpenAI API key is valid and has sufficient credits
   - Check that the key is entered correctly (starts with `sk-`)

2. **Video Loading Issues**
   - Ensure internet connection is stable
   - Some videos might be region-restricted

3. **Slow Response Times**
   - Large explanations might take a few seconds to generate
   - Consider the OpenAI API rate limits

### Error Recovery
- The app includes fallback mechanisms for AI failures
- Basic functionality continues even if some features are unavailable

## 🌟 **Future Enhancements**

- **Multiple Language Support** - Telugu, Hindi, English
- **Voice Interaction** - Speech-to-text for questions
- **Advanced Analytics** - ML-powered learning insights
- **Offline Mode** - Cached content for offline learning
- **Parent Dashboard** - Progress monitoring for parents
- **Collaborative Learning** - Student interaction features

## 📞 **Support**

For technical issues or suggestions:
- Check the troubleshooting section above
- Ensure all dependencies are correctly installed
- Verify your OpenAI API key is valid

## 📄 **License**

This project is designed for educational purposes and follows AP State Board curriculum guidelines.

## 🎉 **Getting Started**

Ready to transform learning? 

1. Set up the environment
2. Get your OpenAI API key
3. Run the app
4. Start your AI-powered learning journey!

**Happy Learning! 🚀📚**
