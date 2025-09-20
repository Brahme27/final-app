import streamlit as st
import openai
from langchain.prompts import PromptTemplate
# from langchain.memory import ConversationBufferMemory  # Deprecated
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import base64
from PIL import Image
import io
import json
from datetime import datetime
import os

# Check OpenAI version and handle compatibility
try:
    from openai import OpenAI
    OPENAI_V1 = True
except ImportError:
    OPENAI_V1 = False

def check_requirements():
    """Check if required packages are installed and return OpenAI version"""
    try:
        import openai
        return openai.__version__
    except ImportError:
        return None

# Page configuration
st.set_page_config(
    page_title="Intelligent Exam Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1a237e 0%, #4a148c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .question-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1a237e;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    .evaluation-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1b5e20;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    .marks-display {
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
    }
    /* Additional styles for better text contrast */
    .question-box strong, .evaluation-box strong {
        color: #1a237e;
        font-weight: 600;
    }
    .question-box p, .evaluation-box p {
        color: #212529;
        line-height: 1.6;
        margin: 0.5rem 0;
        font-weight: 500;
    }
    h3, h4 {
        color: #1a237e;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class ExamAssistant:
    def __init__(self, api_key):
        # Handle different OpenAI library versions
        if OPENAI_V1:
            self.client = OpenAI(api_key=api_key)
        else:
            openai.api_key = api_key
            self.client = None
        
        self.api_key = api_key
        # Simple conversation history instead of deprecated ConversationBufferMemory
        self.conversation_history = []
        
        # Question generation prompt template
        self.question_prompt = PromptTemplate(
            input_variables=["topic", "marks", "variation_seed", "class_level", "subject"],
            template="""
            Generate a UNIQUE, creative, exam-style question on the topic "{topic}" worth exactly {marks} marks.
            Class: {class_level}, Subject: {subject}
            
            VARIATION REQUIREMENT: Create a DIFFERENT question each time, even for the same topic and marks.
            Use the variation seed {variation_seed} to ensure uniqueness.
            
            MANDATORY SPECIAL CASE - If Class is "Class 10" AND Subject "Social Studies" AND marks is 8:
            You MUST ONLY generate questions using these EXACT simple formats given below.
            
            Format 1: "Write down the advantages and disadvantages of [specific aspect related to {topic}]."
            Example: "Write down the advantages and disadvantages of the people when they migrate."
            
            Format 2: "How does [social issue] affect when [relevant context related to {topic}]?"
            Example: "How does gender bias affect when the women work outside of the homes?"
            
            Format 3: "Read the following paragraph and write your opinion on it.
            *Paragraph:*
            [Write a 3-4 line paragraph about {topic} covering social/economic/political aspects]"
            
            Format 4: "Prepare a pamphlet on importance of [aspect related to {topic}]."
            Example: "Prepare a pamphlet on importance of food security."
            
            CRITICAL: For Class 10 Social Studies 8-mark questions, IGNORE all other 8-mark formats below. Use ONLY the 4 simple formats above with the exact phrasing structure shown in examples.
            
            For ALL OTHER cases (different class, subject, or marks), use the standard formats below:
            
            - For 2 marks: Choose from these varied approaches:
              * Definition: "Define {topic}." / "What is meant by {topic}?"
              * Identification: "Identify the main features of {topic}." / "List two key characteristics of {topic}."
              * Basic explanation: "Briefly explain {topic}." / "State the significance of {topic}."
              * Classification: "Classify {topic} and give reasons." / "Categorize the types of {topic}."
            
            - For 4 marks: Choose from these varied approaches:
              * Explanation with examples: "Explain {topic} with suitable examples."
              * Comparison: "Compare and contrast different aspects of {topic}."
              * Application: "How is {topic} applied in real-life situations? Explain."
              * Process description: "Describe the process/mechanism of {topic}."
              * Cause and effect: "Explain the causes and effects related to {topic}."
              * Problem-solving: "Solve a problem related to {topic} step by step."
            
            - For 8 marks (NOT for Class 10 Social Studies 8 marks): Choose from these comprehensive approaches:
              * Deep analysis: "Analyze the concept of {topic} in detail. Discuss its key features, significance, and real-world applications. Evaluate its advantages and disadvantages with suitable examples."
              * Critical examination: "Critically examine {topic}. Explain its fundamental principles, analyze its importance, and discuss its various applications with detailed examples."
              * Comprehensive discussion: "Discuss {topic} comprehensively. Analyze its key components, evaluate its significance, and examine its practical applications in different scenarios."
              * Multi-perspective analysis: "Evaluate {topic} from multiple perspectives. Analyze its theoretical framework, practical implications, and societal impact. Discuss its advantages, limitations, and future prospects."
              * Case study approach: "Using {topic} as a case study, analyze its development, current status, and future potential. Discuss the challenges and opportunities associated with it."
              * Research-based question: "Investigate the role of {topic} in modern society. Analyze its evolution, current applications, and predict its future developments with supporting evidence."
            
            Generate ONLY the question text. For Class 10 Social Studies 8-mark questions, use SIMPLE and DIRECT language as shown in the mandatory formats above with the EXACT phrasing structure.
            """
        )
        
        # Answer evaluation prompt template
        self.evaluation_prompt = PromptTemplate(
            input_variables=["topic", "marks", "question"],
            template="""
            You are an intelligent grading assistant. You will receive an image of a handwritten answer.
            
            Context:
            - Topic: {topic}
            - Question: {question}
            - Total marks: {marks}
            
            Your task:
            1. Extract the handwritten text from the image as accurately as possible
            2. Provide a comprehensive correct/model answer for the question
            3. Evaluate the answer's correctness, clarity, and completeness
            4. Award marks out of {marks} based on standard academic grading criteria
            5. Provide constructive feedback explaining the marks awarded
            
            Grading criteria:
            - Accuracy of content (40%)
            - Completeness of answer (30%)
            - Clarity and organization (20%)
            - Use of relevant examples/details (10%)
            
            IMPORTANT: Do not use any HTML tags or markdown formatting in your response.
            
            Respond in the following JSON format:
            {{
                "extracted_text": "The text you extracted from the handwritten image",
                "correct_answer": "A comprehensive model answer that fully addresses the question for {marks} marks",
                "evaluation": "Your detailed evaluation of the answer",
                "marks_awarded": X,
                "total_marks": {marks},
                "feedback": "Constructive feedback explaining why these marks were given",
                "strengths": ["List of strengths in the answer"],
                "improvements": ["Areas for improvement"]
            }}
            """
        )
    
    def generate_class10_social_studies_8mark_question(self, topic):
        """Generate Class 10 Social Studies 8-mark questions using AI to ensure topic relevance and proper formatting"""
        try:
            # Initialize OpenAI client
            if not hasattr(self, 'client') or self.client is None:
                self.client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
            
            # Add randomization for variety
            import random
            from datetime import datetime
            
            # Create variation elements to ensure different questions each time
            current_time = datetime.now()
            random_seed = random.randint(1000, 9999)
            variation_elements = [
                f"Question variation #{random_seed}",
                f"Generated at {current_time.strftime('%H:%M:%S')}",
                random.choice(['analytical', 'practical', 'theoretical', 'comprehensive', 'detailed']),
                random.choice(['modern context', 'contemporary society', 'current scenario', 'present-day situation']),
                random.choice(['students should analyze', 'learners must evaluate', 'pupils need to examine', 'candidates should assess'])
            ]
            
            # Randomly select format emphasis for variety
            format_styles = [
                {
                    "emphasis": "advantages and disadvantages",
                    "instruction": "Focus on creating an advantages-disadvantages question",
                    "example": "Write down the advantages and disadvantages of the people when they migrate."
                },
                {
                    "emphasis": "cause and effect",
                    "instruction": "Focus on creating a cause-effect relationship question",
                    "example": "How does gender bias affect when the women work outside of the homes?"
                },
                {
                    "emphasis": "opinion and analysis",
                    "instruction": "Focus on creating a paragraph analysis question",
                    "example": "Read the following paragraph and write your opinion on it."
                },
                {
                    "emphasis": "pamphlet creation",
                    "instruction": "Focus on creating a pamphlet preparation question",
                    "example": "Prepare a pamphlet on importance of food security."
                }
            ]
            
            # Randomly select a format style for variation
            selected_style = random.choice(format_styles)
            
            # Add contextual variations for the same topic
            topic_contexts = [
                f"{topic} in rural areas",
                f"{topic} in urban development",
                f"{topic} and economic growth",
                f"{topic} and social change",
                f"{topic} in modern India",
                f"{topic} and sustainable development",
                f"{topic} and government policies",
                f"{topic} and community welfare"
            ]
            
            # Sometimes use the base topic, sometimes use a context variation
            topic_variant = random.choice([topic, random.choice(topic_contexts)])
            
            # Create a dynamic, randomized prompt
            prompt = f"""
You are an expert Class 10 Social Studies teacher creating 8-mark examination questions. 
{variation_elements[2].capitalize()} approach required.

Generate ONE unique question about: "{topic_variant}"
{selected_style['instruction']} but you may use any of the 4 formats if more suitable.

STRICT REQUIREMENTS:
1. The question MUST follow one of these 4 exact formats:
   - "Write down the advantages and disadvantages of [topic-relevant phrase]."
   - "How does [social factor] affect when [topic-relevant context]?"
   - "Read the following paragraph and write your opinion on it.\n*Paragraph:*\n[topic-relevant paragraph]"
   - "Prepare a pamphlet on importance of [topic-relevant aspect]."

2. Make it specifically relevant to "{topic}" in {variation_elements[3]}
3. Use proper Social Studies terminology and concepts
4. Ensure {variation_elements[4]} the topic thoroughly (8-mark level)
5. Make it engaging for Class 10 students
6. Connect to real-world applications

PREFERRED STYLE: {selected_style['emphasis']}
EXAMPLE: {selected_style['example']}

Variation ID: {variation_elements[0]} | Time: {variation_elements[1]}

Generate ONE unique question following the exact format. Make it directly related to "{topic}" and suitable for Class 10 Social Studies.

Return ONLY the question text, no additional explanation.
"""

            # Use higher temperature and add seed for more variation
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are an expert Class 10 Social Studies teacher generating unique questions. Current session: {random_seed}. Ensure variety in question generation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=350,
                temperature=0.9,  # Higher temperature for more variety
                top_p=0.9,       # Add top_p for additional randomness
                frequency_penalty=0.3,  # Reduce repetitive patterns
                presence_penalty=0.3    # Encourage new topics/approaches
            )
            
            generated_question = response.choices[0].message.content.strip()
            
            # Basic validation to ensure the question follows one of the required formats
            format_keywords = [
                "advantages and disadvantages",
                "How does",
                "Read the following paragraph",
                "Prepare a pamphlet"
            ]
            
            # Check if the generated question contains at least one format keyword
            if any(keyword.lower() in generated_question.lower() for keyword in format_keywords):
                return generated_question
            else:
                # Fallback: if the AI didn't follow format, create a topic-specific question using one format
                return self._generate_fallback_question(topic)
                
        except Exception as e:
            st.error(f"Error generating AI question: {str(e)}")
            # Fallback to a manually created question
            return self._generate_fallback_question(topic)
    
    def _generate_fallback_question(self, topic):
        """Generate a fallback question when AI generation fails"""
        import random
        from datetime import datetime
        
        # Add time-based and random elements for variety
        current_time = datetime.now()
        time_seed = int(current_time.strftime('%S')) + random.randint(1, 100)
        
        # Multiple variations for each format to ensure variety
        fallback_formats = [
            # Advantages-Disadvantages variations
            f"Write down the advantages and disadvantages of {topic.lower()} in modern society.",
            f"Write down the advantages and disadvantages of implementing {topic.lower()} in rural areas.",
            f"Write down the advantages and disadvantages of {topic.lower()} for economic development.",
            f"Write down the advantages and disadvantages when communities adopt {topic.lower()}.",
            
            # Cause-Effect variations  
            f"How does {topic.lower()} affect when communities try to achieve sustainable development?",
            f"How does government policy on {topic.lower()} affect when people plan for their future?",
            f"How does {topic.lower()} affect when society undergoes modernization?",
            f"How does {topic.lower()} affect when regions focus on economic growth?",
            
            # Pamphlet variations
            f"Prepare a pamphlet on importance of {topic.lower()} for social and economic development.",
            f"Prepare a pamphlet on importance of {topic.lower()} in modern India.",
            f"Prepare a pamphlet on importance of understanding {topic.lower()} for students.",
            f"Prepare a pamphlet on importance of {topic.lower()} for sustainable future.",
            
            # Paragraph variations
            f"Read the following paragraph and write your opinion on it.\n*Paragraph:*\n{topic} plays a crucial role in shaping society and economy. It influences various aspects of human life including social relationships, economic activities, and environmental sustainability. Understanding {topic.lower()} helps us make better decisions for community development and individual growth.",
            f"Read the following paragraph and write your opinion on it.\n*Paragraph:*\n{topic} has become increasingly important in modern India. It affects how people live, work, and interact with each other. The government and citizens must work together to ensure that {topic.lower()} contributes positively to national development and social welfare.",
            f"Read the following paragraph and write your opinion on it.\n*Paragraph:*\n{topic} is a key factor in determining the progress of any nation. It impacts economic growth, social harmony, and environmental protection. Young people especially need to understand {topic.lower()} to become responsible citizens and contribute to building a better future.",
        ]
        
        # Use time and random elements to select different questions
        selection_index = (time_seed + random.randint(1, 50)) % len(fallback_formats)
        return fallback_formats[selection_index]
    
    def generate_question(self, topic, marks, class_level=None, subject=None):
        """Generate an exam question based on topic and marks"""
        try:
            # Special handling for Class 10 Social Studies 8-mark questions
            if (class_level == "Class 10" and 
                subject and "Social" in subject and 
                marks == 8):
                # Use the dedicated function for exact format
                question = self.generate_class10_social_studies_8mark_question(topic)
                
                # Store in conversation history
                from datetime import datetime
                current_time = datetime.now()
                self.conversation_history.append({
                    "input": f"Generate Class 10 Social Studies question for {topic} ({marks} marks)",
                    "output": question,
                    "timestamp": current_time.isoformat()
                })
                
                return question
            
            # For all other cases, use the existing AI-based generation
            # Import random and datetime for variation
            import random
            from datetime import datetime
            
            # Create a variation seed based on current time and random elements
            current_time = datetime.now()
            random_elements = [
                random.randint(1, 1000),
                random.choice(['creative', 'analytical', 'practical', 'theoretical', 'innovative']),
                random.choice(['detailed', 'comprehensive', 'focused', 'broad', 'specific']),
                current_time.strftime("%H%M%S")
            ]
            variation_seed = f"{'-'.join(map(str, random_elements))}"
            
            # Format prompt with variation seed and additional parameters
            prompt = self.question_prompt.format(
                topic=topic, 
                marks=marks, 
                variation_seed=variation_seed,
                class_level=class_level or "Unknown",
                subject=subject or "Unknown"
            )
            
            # Adjust max_tokens based on mark allocation
            # Higher mark questions need more detailed prompts and responses
            if marks >= 8:
                max_tokens = 1000
            elif marks >= 4:
                max_tokens = 700
            else:
                max_tokens = 500
            
            # Increase temperature for more creative and varied responses
            temperature = 0.9  # Higher temperature for more variation
            
            if OPENAI_V1:
                # Enhanced system message for better question generation with variation emphasis
                system_message = """You are an experienced educator creating diverse exam questions. 
                CRITICAL: Generate UNIQUE, VARIED questions every time, even for the same topic and marks.
                
                SPECIAL MANDATORY RULE: If the input specifies "Class 10" and subject contains "Social" and marks is 8:
                - COMPLETELY IGNORE all analytical 8-mark formats 
                - Use ONLY the 4 simple formats provided: advantages/disadvantages, how does X affect Y, paragraph opinion, or pamphlet
                - Keep the language simple and direct as shown in examples
                - DO NOT use words like "analyze", "critically examine", "evaluate", "comprehensive"
                - DO NOT create long complex questions
                
                For all other cases, use creative approaches, different question styles, and varied vocabulary.
                Avoid repetitive patterns and ensure each question feels fresh and engaging.
                Consider different perspectives, contexts, and applications of the topic."""
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                question = response.choices[0].message.content.strip()
            else:
                # Enhanced system message for better question generation with variation emphasis
                system_message = """You are an experienced educator creating diverse exam questions. 
                CRITICAL: Generate UNIQUE, VARIED questions every time, even for the same topic and marks.
                
                SPECIAL MANDATORY RULE: If the input specifies "Class 10" and subject contains "Social" and marks is 8:
                - COMPLETELY IGNORE all analytical 8-mark formats 
                - Use ONLY the 4 simple formats provided: advantages/disadvantages, how does X affect Y, paragraph opinion, or pamphlet
                - Keep the language simple and direct as shown in examples
                - DO NOT use words like "analyze", "critically examine", "evaluate", "comprehensive"
                - DO NOT create long complex questions
                
                For all other cases, use creative approaches, different question styles, and varied vocabulary.
                Avoid repetitive patterns and ensure each question feels fresh and engaging.
                Consider different perspectives, contexts, and applications of the topic."""
                
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",  # Fallback to gpt-4o-mini for older versions
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                question = response['choices'][0]['message']['content'].strip()
            
            # Additional validation for the generated question
            if not question or len(question.strip()) < 10:
                # Enhanced fallback with variation
                fallback_options = self._get_fallback_questions(topic, marks, class_level, subject)
                question = random.choice(fallback_options)
                st.warning(f"⚠️ Using fallback question for {marks} marks due to API response issue.")
            
            # Additional validation specifically for 8-mark questions (except Class 10 Social Studies)
            elif (marks == 8 and not (class_level == "Class 10" and subject and "Social" in subject)):
                # Check if the 8-mark question is comprehensive enough
                question_lower = question.lower()
                comprehensive_words = ['analyze', 'analyse', 'discuss', 'evaluate', 'examine', 'critically', 'comprehensively', 'detail', 'detailed']
                multiple_aspects = ['features', 'applications', 'examples', 'advantages', 'disadvantages', 'significance', 'importance', 'principles', 'components']
                
                has_comprehensive_words = any(word in question_lower for word in comprehensive_words)
                has_multiple_aspects = sum(1 for word in multiple_aspects if word in question_lower) >= 2
                is_long_enough = len(question.split()) >= 15  # At least 15 words for 8 marks
                
                if not (has_comprehensive_words and has_multiple_aspects and is_long_enough):
                    # Use enhanced fallback for 8-mark questions with variation
                    enhanced_8mark_options = self._get_enhanced_8mark_questions(topic)
                    question = random.choice(enhanced_8mark_options)
                    st.info(f"🔄 Enhanced question complexity for 8 marks requirement.")
            
            # Store in conversation history with timestamp for tracking
            self.conversation_history.append({
                "input": f"Generate question for {topic} ({marks} marks) - {variation_seed}",
                "output": question,
                "timestamp": current_time.isoformat()
            })
            
            return question
            
        except Exception as e:
            # Enhanced error reporting with varied fallback
            error_msg = f"Error generating {marks}-mark question for '{topic}': {str(e)}"
            st.error(error_msg)
            
            # Special handling for Class 10 Social Studies 8-mark questions even in fallback
            if (class_level == "Class 10" and 
                subject and "Social" in subject and 
                marks == 8):
                fallback_question = self.generate_class10_social_studies_8mark_question(topic)
            else:
                # Provide varied fallback questions for other cases
                fallback_options = self._get_fallback_questions(topic, marks, class_level, subject)
                fallback_question = random.choice(fallback_options)
                
            st.info(f"🔄 Using fallback question: {fallback_question}")
            return fallback_question
    
    def _get_fallback_questions(self, topic, marks, class_level=None, subject=None):
        """Get varied fallback questions based on marks"""
        # Special handling for Class 10 Social Studies 8-mark questions
        if (marks == 8 and 
            class_level == "Class 10" and 
            subject and "Social" in subject):
            # Return the specialized question directly
            return [self.generate_class10_social_studies_8mark_question(topic)]
        elif marks == 8:
            return self._get_enhanced_8mark_questions(topic)
        elif marks == 4:
            return [
                f"Explain the concept of {topic} and provide relevant examples. (4 marks)",
                f"Describe {topic} in detail with suitable illustrations. (4 marks)",
                f"How does {topic} work? Explain with examples. (4 marks)",
                f"Compare and contrast the key aspects of {topic}. (4 marks)",
                f"Analyze the importance of {topic} in practical applications. (4 marks)",
                f"Discuss the role and significance of {topic}. (4 marks)"
            ]
        else:  # 2 marks
            return [
                f"Define {topic}. (2 marks)",
                f"What is meant by {topic}? (2 marks)",
                f"State the significance of {topic}. (2 marks)",
                f"List the main features of {topic}. (2 marks)",
                f"Identify the key characteristics of {topic}. (2 marks)",
                f"Briefly explain {topic}. (2 marks)"
            ]
    
    def _get_enhanced_8mark_questions(self, topic):
        """Get varied 8-mark questions with different approaches"""
        return [
            f"Analyze and evaluate the concept of {topic} comprehensively. Discuss its key principles, significance, and practical applications in detail. Examine its advantages and disadvantages with suitable examples. Critically assess its importance in real-world scenarios. (8 marks)",
            f"Critically examine {topic} from multiple perspectives. Explain its fundamental principles, analyze its importance in modern context, and discuss its various applications with detailed examples. Evaluate its impact on society and future prospects. (8 marks)",
            f"Investigate the role of {topic} in contemporary society. Analyze its development, current applications, and potential future implications. Discuss the challenges and opportunities associated with it, supported by relevant examples. (8 marks)",
            f"Evaluate {topic} as a comprehensive case study. Analyze its theoretical framework, practical implementation, and societal impact. Discuss its advantages, limitations, and scope for improvement with detailed justification. (8 marks)",
            f"Discuss {topic} comprehensively from both theoretical and practical viewpoints. Analyze its key components, evaluate its significance in different contexts, and examine its applications across various fields with supporting examples. (8 marks)",
            f"Critically analyze the evolution and current status of {topic}. Evaluate its historical development, present-day applications, and future potential. Discuss the factors influencing its effectiveness and suggest improvements. (8 marks)"
        ]
    
    def encode_image(self, image):
        """Encode image to base64"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    def evaluate_handwritten_answer(self, image, topic, marks, question):
        """Evaluate handwritten answer from image"""
        try:
            # Encode image
            base64_image = self.encode_image(image)
            
            # Create evaluation prompt
            prompt = self.evaluation_prompt.format(
                topic=topic, 
                marks=marks, 
                question=question
            )
            
            if OPENAI_V1:
                # For OpenAI v1.x with vision support
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are an expert grading assistant capable of reading handwritten text and providing fair, constructive evaluations."
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}",
                                        "detail": "high"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                result_text = response.choices[0].message.content.strip()
            else:
                # For older OpenAI versions, use text-only approach
                st.warning("Vision capabilities require OpenAI v1.0+. Using text-only evaluation.")
                text_prompt = f"""
                {prompt}
                
                Note: Image analysis not available. Please provide the student's written answer as text for evaluation.
                """
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert grading assistant."},
                        {"role": "user", "content": text_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                result_text = response['choices'][0]['message']['content'].strip()
            
            # Try to parse JSON response
            try:
                # Extract JSON from the response (in case there's additional text)
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_text = result_text[json_start:json_end]
                    result = json.loads(json_text)
                else:
                    raise ValueError("No JSON found in response")
            except:
                # Fallback if JSON parsing fails
                result = {
                    "extracted_text": "Could not extract text clearly" if OPENAI_V1 else "Text analysis not available - please upgrade OpenAI library",
                    "evaluation": result_text,
                    "marks_awarded": 0,
                    "total_marks": marks,
                    "feedback": "Please ensure the handwriting is clear and try again." if OPENAI_V1 else "Vision analysis requires OpenAI v1.0+",
                    "strengths": [],
                    "improvements": ["Improve handwriting clarity"] if OPENAI_V1 else ["Upgrade OpenAI library for image analysis"]
                }
            
            # Store in conversation history
            self.conversation_history.append({
                "input": f"Evaluate answer for {topic}",
                "output": f"Awarded {result.get('marks_awarded', 0)}/{marks} marks"
            })
            
            return result
            
        except Exception as e:
            st.error(f"Error evaluating answer: {str(e)}")
            return None

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📚 Intelligent Exam Assistant</h1>
        <p>Generate exam questions and evaluate handwritten answers with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for API key and settings
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Display version information
        openai_version = check_requirements()
        if openai_version:
            version_color = "🟢" if OPENAI_V1 else "🟡"
            st.info(f"{version_color} OpenAI version: {openai_version}")
            if not OPENAI_V1:
                st.warning("⚠️ For full vision capabilities, please upgrade: `pip install openai>=1.0.0`")
        else:
            st.error("❌ OpenAI not installed. Please install: `pip install openai`")
        
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password",
            help="Enter your OpenAI API key to use GPT-4o mini"
        )
        
        if not api_key:
            st.warning("Please enter your OpenAI API key to continue.")
            st.info("""
            **Required packages:**
            ```
            pip install streamlit
            pip install openai>=1.0.0
            pip install langchain
            pip install pillow
            ```
            """)
            st.stop()
        
        st.header("📊 Session History")
        if st.button("Clear History"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Initialize the assistant
    try:
        if 'assistant' not in st.session_state:
            st.session_state.assistant = ExamAssistant(api_key)
    except Exception as e:
        st.error(f"Error initializing assistant: {str(e)}")
        st.info("Please check your OpenAI API key and internet connection.")
        st.stop()
    
    # Main interface tabs
    tab1, tab2 = st.tabs(["📝 Question Generator", "✍️ Answer Evaluator"])
    
    with tab1:
        st.header("Generate Exam Questions")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            topic = st.text_input(
                "Enter the topic/subject:",
                placeholder="e.g., Photosynthesis, World War II, Quadratic Equations",
                help="Be specific about the topic you want to create a question for"
            )
        
        with col2:
            marks = st.selectbox(
                "Select marks:",
                options=[2, 4, 8],
                help="Choose the mark allocation for the question"
            )
        
        # Additional inputs for class and subject
        col3, col4 = st.columns([1, 1])
        
        with col3:
            class_level = st.selectbox(
                "Select class:",
                options=["Class 6", "Class 7", "Class 8", "Class 9", "Class 10", "Class 11", "Class 12"],
                index=4,  # Default to Class 10
                help="Select the class level for the question"
            )
        
        with col4:
            subject = st.selectbox(
                "Select subject:",
                options=["Mathematics", "Science", "Social Studies", "English", "Hindi", "Physics", "Chemistry", "Biology", "History", "Geography", "Political Science", "Economics"],
                index=2,  # Default to Social Studies
                help="Select the subject for the question"
            )
        
        if st.button("🎯 Generate Question", type="primary"):
            if topic:
                with st.spinner("Generating question..."):
                    question = st.session_state.assistant.generate_question(topic, marks, class_level, subject)
                    
                    if question:
                        st.session_state.current_question = question
                        st.session_state.current_topic = topic
                        st.session_state.current_marks = marks
                        
                        st.markdown(f"""
                        <div class="question-box">
                            <h3>📋 Generated Question ({marks} marks)</h3>
                            <p><strong>Topic:</strong> {topic}</p>
                            <p><strong>Question:</strong> {question}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.success("Question generated successfully! You can now evaluate answers in the next tab.")
            else:
                st.error("Please enter a topic first.")
    
    with tab2:
        st.header("Evaluate Handwritten Answers")
        
        # Check if we have a current question
        if 'current_question' not in st.session_state:
            st.info("💡 Please generate a question first in the Question Generator tab.")
        else:
            # Display current question
            st.markdown(f"""
            <div class="question-box">
                <h3>📋 Current Question ({st.session_state.current_marks} marks)</h3>
                <p><strong>Topic:</strong> {st.session_state.current_topic}</p>
                <p><strong>Question:</strong> {st.session_state.current_question}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # File uploader for handwritten answer
            uploaded_file = st.file_uploader(
                "Upload image of handwritten answer",
                type=['png', 'jpg', 'jpeg'],
                help="Upload a clear image of the handwritten answer"
            )
            
            if uploaded_file is not None:
                # Display uploaded image
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("📷 Uploaded Answer")
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Handwritten Answer", use_container_width=True)
                
                # Evaluate button
                if st.button("🔍 Evaluate Answer", type="primary"):
                    with st.spinner("Analyzing handwritten answer..."):
                        evaluation = st.session_state.assistant.evaluate_handwritten_answer(
                            image,
                            st.session_state.current_topic,
                            st.session_state.current_marks,
                            st.session_state.current_question
                        )
                        
                        if evaluation:
                            with col2:
                                st.subheader("📊 Evaluation Results")
                                
                                # Marks display with detailed breakdown
                                marks_awarded = evaluation.get('marks_awarded', 0)
                                total_marks = evaluation.get('total_marks', st.session_state.current_marks)
                                percentage = (marks_awarded / total_marks) * 100 if total_marks > 0 else 0
                                
                                st.markdown(f"""
                                <div class="marks-display">
                                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">
                                        {marks_awarded} / {total_marks}
                                    </div>
                                    <div style="font-size: 1.25rem; color: #4a5568;">
                                        {percentage:.1f}%
                                    </div>
                                    <div style="margin-top: 1rem; height: 8px; background-color: #e2e8f0; border-radius: 4px;">
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
                            
                            # Detailed evaluation
                            st.subheader("📝 Detailed Evaluation")
                            
                            with st.expander("Show Extracted Text", expanded=True):
                                st.write(f"*{evaluation.get('extracted_text', 'N/A')}*")
                            
                            with st.expander("Evaluation", expanded=True):
                                st.write(evaluation.get('evaluation', 'N/A'))
                            
                            if evaluation.get('correct_answer'):
                                with st.expander("✅ Correct Answer", expanded=True):
                                    st.success("**Model Answer:**")
                                    st.write(evaluation.get('correct_answer', 'N/A'))
                            
                            with st.expander("Feedback", expanded=True):
                                st.write(evaluation.get('feedback', 'N/A'))
                            
                            # Strengths and improvements
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if evaluation.get('strengths'):
                                    st.success("**Strengths:**")
                                    for strength in evaluation['strengths']:
                                        st.write(f"✅ {strength}")
                            
                            with col2:
                                if evaluation.get('improvements'):
                                    st.info("**Areas for Improvement:**")
                                    for improvement in evaluation['improvements']:
                                        st.write(f"📈 {improvement}")
                            
                            # Store evaluation in session
                            if 'evaluations' not in st.session_state:
                                st.session_state.evaluations = []
                            
                            st.session_state.evaluations.append({
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'topic': st.session_state.current_topic,
                                'question': st.session_state.current_question,
                                'marks': f"{evaluation.get('marks_awarded', 0)}/{evaluation.get('total_marks', st.session_state.current_marks)}",
                                'evaluation': evaluation
                            })
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: gray;'>🤖 Powered by OpenAI GPT-4o mini | Built with Streamlit & LangChain</p>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()