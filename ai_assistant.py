"""
AI Assistant Module
Handles all AI-powered educational content generation with proper LaTeX formatting
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import openai
import re
from typing import Dict, List, Any, Optional
from curriculum_data import get_curriculum_data

class AIAssistant:
    def __init__(self, api_key: str):
        """Initialize AI Assistant with OpenAI API key"""
        self.api_key = api_key
        self.llm = ChatOpenAI(
            api_key=api_key,
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=4000
        )
        self.curriculum_data = get_curriculum_data()
    
    def get_curriculum_context(self, topic: str, subject: str, class_level: str) -> str:
        """Get relevant curriculum context for the topic"""
        try:
            curriculum = self.curriculum_data.get(class_level, {})
            subject_data = curriculum.get(subject, {})
            
            relevant_context = ""
            for chapter, topics in subject_data.items():
                if topic in topics:
                    relevant_context += f"Chapter: {chapter}\n"
                    relevant_context += f"Related topics in this chapter: {', '.join(topics)}\n"
                    break
            
            return relevant_context
        except Exception:
            return ""
    
    def generate_topic_explanation(self, topic: str, subject: str, class_level: str, user_preferences: Optional[Dict] = None) -> str:
        """Generate a comprehensive topic explanation suitable for the student's grade level"""
        
        curriculum_context = self.get_curriculum_context(topic, subject, class_level)
        
        # Subject-specific LaTeX formatting guidelines
        latex_guidelines = self._get_latex_guidelines(subject, topic, class_level)
        
        # Curriculum alignment requirements
        curriculum_guidelines = ""
        if curriculum_context:
            curriculum_guidelines = f"""
        
        AP STATE BOARD CURRICULUM CONTEXT:
        {curriculum_context}
        
        CURRICULUM ALIGNMENT REQUIREMENTS:
        - Strictly follow AP State Board syllabus standards for {class_level}
        - Reference content as it appears in AP State Board textbooks
        - Use terminology and notation consistent with AP State Board materials
        - Include all topics and subtopics as per the curriculum structure
        - Ensure age-appropriate depth matching the class level expectations
        """
        
        system_prompt = self._build_system_prompt(subject, topic, class_level, latex_guidelines, curriculum_guidelines, user_preferences)
        human_prompt = self._build_human_prompt(topic, subject, class_level, curriculum_context, user_preferences)
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"🚫 Sorry, I couldn't generate the explanation right now. Error: {str(e)}"
    
    def _get_latex_guidelines(self, subject: str, topic: str, class_level: str) -> str:
        """Get subject-specific LaTeX formatting guidelines"""
        
        if subject.lower() in ['mathematics', 'math', 'maths']:
            return f"""
        
        MATHEMATICS LATEX FORMATTING - CRITICAL REQUIREMENTS:
        📐 ALL mathematical formulas MUST use proper LaTeX notation:
        
        BASIC FORMATTING:
        - Display equations: $$equation$$  (Example: $$a^2 + b^2 = c^2$$)
        - Inline math: $equation$  (Example: The area is $A = \\pi r^2$)
        
        FRACTIONS - CORRECT FORMAT:
        - Simple fractions: $$\\frac{{a}}{{b}}$$
        - Complex fractions: $$\\frac{{numerator}}{{denominator}}$$
        - Examples: $$\\frac{{1}}{{2}}$$, $$\\frac{{x+1}}{{x-1}}$$, $$\\frac{{dy}}{{dx}}$$
        
        COMMON MATHEMATICAL EXPRESSIONS:
        - Powers: $$x^2$$, $$a^{{n+1}}$$, $$e^{{-x}}$$
        - Roots: $$\\sqrt{{x}}$$, $$\\sqrt[n]{{x}}$$, $$\\sqrt{{a^2 + b^2}}$$
        - Trigonometry: $$\\sin(\\theta)$$, $$\\cos(\\alpha)$$, $$\\tan(\\beta)$$
        - Logarithms: $$\\log(x)$$, $$\\ln(x)$$, $$\\log_{{10}}(x)$$
        - Summation: $$\\sum_{{i=1}}^{{n}} x_i$$
        - Integration: $$\\int_{{a}}^{{b}} f(x)dx$$
        - Differentiation: $$\\frac{{dy}}{{dx}}$$, $$\\frac{{d^2y}}{{dx^2}}$$
        
        GEOMETRY FORMULAS:
        - Area of circle: $$A = \\pi r^2$$
        - Circumference: $$C = 2\\pi r$$
        - Volume of sphere: $$V = \\frac{{4}}{{3}}\\pi r^3$$
        - Pythagorean theorem: $$a^2 + b^2 = c^2$$
        
        ALGEBRA:
        - Quadratic formula: $$x = \\frac{{-b \\pm \\sqrt{{b^2 - 4ac}}}}{{2a}}$$
        - Linear equation: $$y = mx + c$$
        - Factorization: $$(a+b)^2 = a^2 + 2ab + b^2$$
        
        SYMBOLS:
        - Greek letters: $$\\alpha, \\beta, \\gamma, \\delta, \\theta, \\pi, \\omega$$
        - Infinity: $$\\infty$$
        - Approximately: $$\\approx$$
        - Greater/Less than: $$\\geq, \\leq, >, <$$
        """
        
        elif subject.lower() in ['physical science', 'physics', 'science', 'physical sciences']:
            return f"""
        
        PHYSICAL SCIENCE LATEX FORMATTING - CRITICAL REQUIREMENTS:
        🔬 ALL scientific formulas and units MUST use proper LaTeX notation:
        
        BASIC FORMATTING:
        - Display equations: $$equation$$  (Example: $$F = ma$$)
        - Inline math: $equation$  (Example: The force is $F = 10\\text{{ N}}$)
        
        FRACTIONS - CORRECT FORMAT:
        - Simple fractions: $$\\frac{{a}}{{b}}$$
        - Physics examples: $$v = \\frac{{d}}{{t}}$$, $$a = \\frac{{\\Delta v}}{{\\Delta t}}$$
        - Power formula: $$P = \\frac{{W}}{{t}}$$
        - Density: $$\\rho = \\frac{{m}}{{V}}$$
        
        MECHANICS FORMULAS:
        - Newton's laws: $$F = ma$$, $$F_{{net}} = 0$$
        - Kinematic equations: $$v = u + at$$, $$s = ut + \\frac{{1}}{{2}}at^2$$, $$v^2 = u^2 + 2as$$
        - Momentum: $$p = mv$$
        - Work: $$W = F \\cdot d$$
        - Power: $$P = \\frac{{W}}{{t}} = Fv$$
        - Kinetic energy: $$KE = \\frac{{1}}{{2}}mv^2$$
        - Potential energy: $$PE = mgh$$
        
        WAVES AND OPTICS:
        - Wave equation: $$v = f\\lambda$$
        - Mirror formula: $$\\frac{{1}}{{f}} = \\frac{{1}}{{u}} + \\frac{{1}}{{v}}$$
        - Magnification: $$m = \\frac{{v}}{{u}} = \\frac{{h'}}{{h}}$$
        - Snell's law: $$\\frac{{\\sin i}}{{\\sin r}} = \\frac{{n_2}}{{n_1}}$$
        
        ELECTRICITY:
        - Ohm's law: $$V = IR$$
        - Power: $$P = VI = I^2R = \\frac{{V^2}}{{R}}$$
        - Resistors in series: $$R_{{total}} = R_1 + R_2 + R_3$$
        - Resistors in parallel: $$\\frac{{1}}{{R_{{total}}}} = \\frac{{1}}{{R_1}} + \\frac{{1}}{{R_2}} + \\frac{{1}}{{R_3}}$$
        
        THERMODYNAMICS:
        - Heat: $$Q = mc\\Delta T$$
        - Ideal gas law: $$PV = nRT$$
        - Efficiency: $$\\eta = \\frac{{W_{{out}}}}{{Q_{{in}}}} \\times 100\\%$$
        
        UNITS (LaTeX format):
        - Force: $\\text{{N}}$ (Newton), $\\text{{kg}} \\cdot \\text{{m/s}}^2$
        - Energy: $\\text{{J}}$ (Joule), $\\text{{kg}} \\cdot \\text{{m}}^2\\text{{/s}}^2$
        - Power: $\\text{{W}}$ (Watt), $\\text{{J/s}}$
        - Pressure: $\\text{{Pa}}$ (Pascal), $\\text{{N/m}}^2$
        - Frequency: $\\text{{Hz}}$ (Hertz), $\\text{{s}}^{{-1}}$
        - Velocity: $\\text{{m/s}}$
        - Acceleration: $\\text{{m/s}}^2$
        - Electric current: $\\text{{A}}$ (Ampere)
        - Voltage: $\\text{{V}}$ (Volt)
        - Resistance: $\\Omega$ (Ohm)
        
        VECTORS:
        - Vector notation: $$\\vec{{F}}$$, $$\\vec{{v}}$$, $$\\vec{{a}}$$
        - Vector addition: $$\\vec{{R}} = \\vec{{A}} + \\vec{{B}}$$
        - Dot product: $$\\vec{{A}} \\cdot \\vec{{B}} = AB\\cos\\theta$$
        
        SYMBOLS:
        - Greek letters: $$\\alpha, \\beta, \\gamma, \\delta, \\theta, \\lambda, \\omega, \\rho, \\eta$$
        - Change: $$\\Delta$$ (Example: $$\\Delta T$$, $$\\Delta v$$)
        - Proportional: $$\\propto$$
        """
        
        else:
            return ""
    
    def _build_system_prompt(self, subject: str, topic: str, class_level: str, latex_guidelines: str, curriculum_guidelines: str, user_preferences: Optional[Dict]) -> str:
        """Build the system prompt for topic explanation"""
        
        system_prompt = f"""
        You are an expert teacher for AP State Board curriculum with deep knowledge of official textbook content. 
        Generate a COMPREHENSIVE, DETAILED explanation for {class_level} students that matches the depth and quality expected from AP State Board textbooks.
        
        CONTENT DEPTH REQUIREMENTS:
        1. Provide extensive, thorough explanations (minimum 1500-2000 words)
        2. Use multiple detailed examples and step-by-step solutions
        3. Include comprehensive background and context
        4. Break down every concept into multiple sub-concepts with full explanations
        5. Provide detailed explanations for each step and reasoning
        6. Include multiple perspectives and approaches to the same concept
        7. Add detailed practice guidance and study tips
        8. Reference official AP State Board curriculum standards
        
        GENERAL GUIDELINES:
        1. Use clear, pedagogical language appropriate for {class_level} students
        2. Include extensive real-world examples and detailed analogies
        3. Break down complex concepts into multiple digestible parts with full explanations
        4. Use emojis and engaging formatting throughout for better readability
        5. Include practical applications with detailed explanations and calculations
        6. Focus on building deep conceptual understanding as per AP State Board methodology
        7. Provide comprehensive coverage as found in official AP State Board textbooks
        8. Include historical context and development of concepts where relevant
        9. Add tips for better understanding and memory retention
        10. Include common misconceptions and clarifications
        11. Connect to previous and upcoming topics in the curriculum
        
        {latex_guidelines}
        {curriculum_guidelines}
        
        Subject: {subject}
        Topic: {topic}
        Class Level: {class_level}
        
        IMPORTANT: Your explanation should be as comprehensive as a textbook chapter, with multiple sections, 
        detailed explanations, extensive examples, and thorough coverage of all aspects of the topic as per 
        AP State Board standards and expectations.
        """
        
        # Add user preference personalization if available
        if user_preferences:
            system_prompt += self._add_personalization_prompt(user_preferences)
        
        return system_prompt
    
    def _add_personalization_prompt(self, user_preferences: Dict) -> str:
        """Add personalization requirements to the system prompt"""
        
        personalization = "\n\n----- IMPORTANT: REQUIRED PERSONALIZATION -----"
        personalization += "\nYou MUST personalize this explanation based on the following student preferences:"
        
        if user_preferences.get('activities'):
            activities = ', '.join(user_preferences['activities'][:3])
            personalization += f"\n- ACTIVITIES: Integrate references, analogies, and examples related to: {activities}"
        
        if user_preferences.get('storytelling_styles'):
            styles = ', '.join(user_preferences['storytelling_styles'][:3])
            personalization += f"\n- STORYTELLING: Structure your explanation using these styles: {styles}"
        
        if user_preferences.get('memory_techniques'):
            techniques = ', '.join(user_preferences['memory_techniques'])
            personalization += f"\n- MEMORY TECHNIQUES: Apply these specific learning techniques throughout: {techniques}"
        
        if user_preferences.get('learning_approach'):
            personalization += f"\n- LEARNING APPROACH: Your explanation MUST follow this approach: {user_preferences['learning_approach']}"
        
        if user_preferences.get('difficulty_preference'):
            personalization += f"\n- DIFFICULTY STRUCTURE: Present information according to this preference: {user_preferences['difficulty_preference']}"
        
        personalization += "\n\nFor each section of your explanation, explicitly incorporate these personalization elements."
        personalization += "\nThis personalization is MANDATORY and should be obvious in your explanation."
        
        return personalization
    
    def _build_human_prompt(self, topic: str, subject: str, class_level: str, curriculum_context: str, user_preferences: Optional[Dict]) -> str:
        """Build the human prompt for topic explanation"""
        
        human_prompt = f"""
        Please provide a DETAILED, COMPREHENSIVE explanation of the topic "{topic}" from {subject} for {class_level} students following the AP State Board syllabus. 
        
        This should be a complete learning resource similar to an official AP State Board textbook chapter with extensive detail and examples.
        
        {f"CURRICULUM CONTEXT: {curriculum_context}" if curriculum_context else ""}
        
        MANDATORY STRUCTURE FOR ALL SUBJECTS:
        1. 🎯 **Introduction & Overview** (Detailed introduction with context, importance, and curriculum placement)
        2. 🔍 **Fundamental Concepts** (Break down ALL key concepts with detailed explanations and definitions)
        3. 📐 **Formulas & Mathematical Content** (For math/science topics: ALL relevant formulas in LaTeX format with derivations)
        4. 📚 **Detailed Theory & Explanations** (Comprehensive theoretical background as per AP State Board textbooks)
        5. 🔢 **Step-by-Step Examples** (Multiple detailed worked examples with complete solutions and explanations)
        6. 🌟 **Real-world Applications** (Extensive practical applications with detailed explanations and relevance)
        7. 💡 **Problem-Solving Strategies** (Detailed approaches, methodologies, and techniques)
        8. 📝 **Important Points & Key Takeaways** (Comprehensive summary of all critical points)
        9. 🎯 **Study Tips & Memory Aids** (Detailed learning strategies, mnemonics, and retention techniques)
        10. 🚀 **Advanced Concepts & Extensions** (Additional related topics and deeper insights for curious learners)
       
        🔴 CRITICAL LATEX FORMATTING REQUIREMENTS:
        For Mathematics and Physical Science topics:
        
        CORRECT LaTeX FORMAT:
        - Display equations: $$\\frac{{{{a}}}}{{{{b}}}}$$ NOT $$\\frac{{a}}{{b}}$$
        - Inline math: $A = \\pi r^2$ NOT $A = \\pi r^2$
        - Fractions: $$\\frac{{{{numerator}}}}{{{{denominator}}}}$$
        - Powers: $$x^{{{{2}}}}$$ for simple, $$x^{{{{n+1}}}}$$ for complex
        - Examples: $$F = ma$$, $$v = \\frac{{{{d}}}}{{{{t}}}}$$, $$a = \\frac{{{{\\Delta v}}}}{{{{\\Delta t}}}}$$
        
        PHYSICS FORMULAS EXAMPLES:
        - $$v = u + at$$
        - $$s = ut + \\frac{{{{1}}}}{{{{2}}}}at^2$$
        - $$F = \\frac{{{{mv^2}}}}{{{{r}}}}$$
        - $$P = \\frac{{{{W}}}}{{{{t}}}}$$
        - $$\\rho = \\frac{{{{m}}}}{{{{V}}}}$$
        - $$\\frac{{{{1}}}}{{{{f}}}} = \\frac{{{{1}}}}{{{{u}}}} + \\frac{{{{1}}}}{{{{v}}}}$$
        
        MATHEMATICS FORMULAS EXAMPLES:
        - $$x = \\frac{{{{-b \\pm \\sqrt{{{{b^2 - 4ac}}}}}}}}{{{{2a}}}}$$
        - $$A = \\pi r^2$$
        - $$V = \\frac{{{{4}}}}{{{{3}}}}\\pi r^3$$
        - $$(a+b)^2 = a^2 + 2ab + b^2$$
        
        UNITS IN LATEX:
        - $\\text{{{{m/s}}}}^2$, $\\text{{{{kg}}}}$, $\\text{{{{N}}}}$, $\\text{{{{J}}}}$, $\\text{{{{W}}}}$, $\\Omega$
        
        This LaTeX formatting is MANDATORY for proper rendering!
        
        CONTENT REQUIREMENTS:
        - Minimum 1500-2000 words of comprehensive, detailed content
        - Multiple detailed examples and case studies with complete LaTeX-formatted solutions
        - Extensive explanations for each concept, formula, and procedure
        - Clear connections between different aspects of the topic
        - Comprehensive coverage matching official AP State Board textbook depth
        - Include prerequisite knowledge review and foundation building
        - Provide connections to other related curriculum topics
        - Use official AP State Board terminology and notation standards
        - Include assessment criteria and learning objectives alignment
        
        Make sure the explanation is thorough, engaging, educationally complete, follows AP State Board standards, 
        and provides students with a comprehensive understanding that could serve as their primary learning resource 
        for this topic, equivalent to or better than their textbook coverage.
        """
        
        # Add personalization reminder if preferences exist
        if user_preferences:
            human_prompt += """
            
            CRITICAL: Your explanation MUST be heavily personalized based on the student's preferences. 
            Make the personalization obvious by:
            1. Choosing examples that directly relate to their interests
            2. Using their preferred storytelling styles throughout
            3. Applying their preferred memory techniques in key points
            4. Following their preferred learning approach
            5. Structuring difficulty according to their preference
            
            The personalization should be evident in every section of your explanation.
            """
        
        return human_prompt
    
    def answer_question(self, question: str, topic: str, subject: str, class_level: str) -> str:
        """Answer student questions about the topic contextually"""
        
        latex_requirements = ""
        if subject.lower() in ['mathematics', 'math', 'maths', 'physical science', 'physics', 'science']:
            latex_requirements = """
            CRITICAL LATEX FORMATTING:
            - Use $$formula$$ for display equations (e.g., $$F = ma$$)
            - Use $formula$ for inline math (e.g., The force is $F = 10\\text{{ N}}$)
            - For fractions: $$\\frac{{numerator}}{{denominator}}$$
            - Include proper units in LaTeX: $\\text{{m/s}}^2$, $\\text{{kg}}$, $\\text{{N}}$, etc.
            - Examples: $$v = \\frac{{d}}{{t}}$$, $$P = \\frac{{W}}{{t}}$$, $$\\rho = \\frac{{m}}{{V}}$$
            """
        
        system_prompt = f"""
        You are a friendly and knowledgeable teacher helping a {class_level} student with {subject}.
        The student is currently learning about "{topic}".
        
        Guidelines:
        1. Answer in a warm, encouraging tone
        2. Use language appropriate for {class_level} students
        3. Connect your answer back to the current topic when possible
        4. Provide examples to clarify concepts
        5. If the question is off-topic, gently guide back to the subject
        6. Use emojis to make responses engaging
        7. Encourage further questions and curiosity
        8. If you don't know something, admit it and suggest how to find the answer
        
        {latex_requirements}
        """
        
        human_prompt = f"""
        Student Question: "{question}"
        
        Current Topic: {topic}
        Subject: {subject}
        Class: {class_level}
        
        Please provide a helpful, encouraging response that addresses the student's question while staying relevant to their current learning context.
        
        {latex_requirements if latex_requirements else ""}
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"🚫 Sorry, I couldn't answer your question right now. Please try again! Error: {str(e)}"
    
    def generate_study_tips(self, topic: str, subject: str, class_level: str) -> str:
        """Generate personalized study tips for the topic"""
        
        system_prompt = f"""
        You are an educational consultant providing study strategies for {class_level} students studying {subject}.
        Focus on practical, actionable study tips that are age-appropriate and effective.
        """
        
        human_prompt = f"""
        Generate specific study tips for learning "{topic}" in {subject} for {class_level} students.
        Include:
        1. 📚 Study techniques
        2. 🧠 Memory aids
        3. ⏰ Time management tips
        4. 🔄 Review strategies
        5. 🎯 Practice suggestions
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"🚫 Sorry, I couldn't generate study tips right now. Error: {str(e)}"
    
    def analyze_learning_strengths_weaknesses(self, quiz_history: List[Dict]) -> str:
        """Analyze student performance and provide insights"""
        
        if not quiz_history:
            return "📊 No quiz data available yet. Take some quizzes to get personalized insights!"
        
        # Calculate basic statistics
        total_quizzes = len(quiz_history)
        total_score = sum(quiz['score'] for quiz in quiz_history)
        total_possible = sum(quiz['total'] for quiz in quiz_history)
        average_percentage = (total_score / total_possible) * 100 if total_possible > 0 else 0
        
        # Find best and worst performing topics
        topic_scores = {}
        for quiz in quiz_history:
            topic = quiz['topic']
            percentage = (quiz['score'] / quiz['total']) * 100 if quiz['total'] > 0 else 0
            if topic not in topic_scores:
                topic_scores[topic] = []
            topic_scores[topic].append(percentage)
        
        # Average scores per topic
        topic_averages = {topic: sum(scores)/len(scores) for topic, scores in topic_scores.items()}
        
        best_topics = sorted(topic_averages.items(), key=lambda x: x[1], reverse=True)[:3]
        weak_topics = sorted(topic_averages.items(), key=lambda x: x[1])[:3]
        
        system_prompt = """
        You are an educational analyst providing personalized learning insights.
        Analyze the student's performance data and provide constructive feedback with actionable recommendations.
        """
        
        human_prompt = f"""
        Analyze this student's learning performance:
        
        📊 Overall Statistics:
        - Total Quizzes Taken: {total_quizzes}
        - Average Score: {average_percentage:.1f}%
        
        🏆 Strongest Topics:
        {chr(10).join([f"- {topic}: {score:.1f}%" for topic, score in best_topics])}
        
        📚 Areas for Improvement:
        {chr(10).join([f"- {topic}: {score:.1f}%" for topic, score in weak_topics])}
        
        Provide:
        1. 👍 Strengths analysis
        2. 📈 Areas for improvement
        3. 🎯 Specific recommendations
        4. 📅 Study plan suggestions
        5. 💪 Motivational feedback
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"🚫 Sorry, I couldn't analyze your performance right now. Error: {str(e)}"
    
    def generate_interactive_hint(self, question: Dict[str, Any], student_input: str, hint_level: int, 
                            subject: str, class_level: str, topic: str) -> str:
        """Generate progressive interactive hints for quiz questions"""
        
        # Extract question components safely
        question_text = question.get('question', '')
        correct_answer = question.get('correct_answer', '')
        all_options = question.get('options', [])
        explanation = question.get('explanation', '')
        
        # Extract key components from the question for analysis
        numerical_values = re.findall(r'\b\d+\.?\d*\b', question_text)
        numerical_values = numerical_values[:3] if numerical_values else []
        
        # Find key subject-specific terms
        question_keywords = self._extract_subject_keywords(question_text, subject)
        
        # Analyze the options to understand the question type
        option_analysis = self._analyze_question_type(all_options, question_text)
        
        # Get LaTeX requirements for math/science subjects
        latex_requirements = self._get_latex_requirements_for_hints(subject)
        
        system_prompt = f"""
        You are an expert tutor for {class_level} students studying {subject}, specifically the topic "{topic}".
        Your goal is to help students solve THIS SPECIFIC QUESTION step by step using progressive hints.
        
        QUESTION ANALYSIS:
        Question: {question_text}
        Options: {all_options}
        Correct Answer: {correct_answer}
        Explanation: {explanation}
        Keywords Found: {question_keywords}
        Numbers Found: {numerical_values}
        Question Type: {option_analysis}
        
        PROGRESSIVE HINT STRATEGY:
        Level 1: Point out SPECIFIC elements in this question (keywords, numbers, concepts) and what to focus on
        Level 2: Guide through the thinking process - what method/approach to use for THIS question
        Level 3: Give more detailed steps, eliminate obviously wrong options, provide partial solution
        Level 4+: Provide complete solution with step-by-step working
        
        CURRENT CONTEXT:
        Student's response: "{student_input}"
        Hint Level: {hint_level}
        
        CRITICAL REQUIREMENTS:
        1. Be SPECIFIC to this question's content - use the actual numbers, terms, and data from the question
        2. Build on the student's previous response if they provided one
        3. Make each hint progressively more revealing
        4. Use encouraging language and emojis
        5. For calculation questions, show the actual calculation steps
        6. For concept questions, break down the concept specifically as it applies to this question
        
        {latex_requirements}
        """
        
        # Generate hint based on level
        if hint_level == 1:
            human_prompt = self._build_hint_level_1(question_text, numerical_values, question_keywords, subject)
        elif hint_level == 2:
            human_prompt = self._build_hint_level_2(student_input, numerical_values, question_keywords)
        elif hint_level == 3:
            human_prompt = self._build_hint_level_3(student_input, all_options, correct_answer)
        else:
            human_prompt = self._build_hint_level_4_plus(student_input, question_text, correct_answer, explanation, topic, numerical_values)
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            return self._generate_fallback_hint(hint_level, question_text, correct_answer, explanation, topic, numerical_values, all_options, question_keywords)
    
    def _extract_subject_keywords(self, question_text: str, subject: str) -> List[str]:
        """Extract subject-specific keywords from the question"""
        
        subject_keywords = {
            'Mathematics': ['calculate', 'solve', 'find', 'area', 'volume', 'percentage', 'fraction', 'decimal', 'equation', 'formula', 'graph', 'angle', 'perimeter'],
            'Science': ['photosynthesis', 'respiration', 'digestion', 'circulation', 'gravity', 'force', 'energy', 'matter', 'chemical', 'physical', 'reaction', 'experiment'],
            'Physical Science': ['force', 'energy', 'power', 'velocity', 'acceleration', 'mass', 'weight', 'density', 'pressure', 'temperature', 'heat', 'light', 'sound', 'electricity'],
            'Physics': ['motion', 'force', 'energy', 'momentum', 'wave', 'optics', 'electricity', 'magnetism', 'thermodynamics'],
            'Environmental Studies': ['pollution', 'conservation', 'ecosystem', 'biodiversity', 'natural resources', 'climate', 'environment', 'sustainable'],
            'English': ['noun', 'verb', 'adjective', 'sentence', 'paragraph', 'story', 'character', 'setting', 'plot', 'theme'],
            'Social Studies': ['history', 'geography', 'government', 'democracy', 'civilization', 'culture', 'society', 'economy', 'trade']
        }
        
        relevant_keywords = subject_keywords.get(subject, [])
        found_keywords = []
        
        for keyword in relevant_keywords:
            if keyword.lower() in question_text.lower():
                found_keywords.append(keyword)
        
        return found_keywords[:3]  # Return max 3 keywords
    
    def _analyze_question_type(self, all_options: List[str], question_text: str) -> str:
        """Analyze the question type based on options and question text"""
        
        if not all_options:
            return "Open-ended question"
        
        options_text = ' '.join(all_options).lower()
        
        if any(char.isdigit() for option in all_options for char in option):
            return "This appears to be a calculation-based question."
        elif any(word in options_text for word in ['is', 'are', 'means', 'refers']):
            return "This appears to be a definition or concept identification question."
        elif any(word in options_text for word in ['first', 'second', 'step', 'process']):
            return "This appears to be about understanding a process or sequence."
        else:
            return "This appears to be a conceptual understanding question."
    
    def _get_latex_requirements_for_hints(self, subject: str) -> str:
        """Get LaTeX requirements for hints in math/science subjects"""
        
        if subject.lower() in ['mathematics', 'math', 'maths', 'physical science', 'physics', 'science']:
            return """
        LATEX FORMATTING FOR HINTS:
        - Display equations: $formula$ (e.g., $F = ma$, $v = \\frac{{d}}{{t}}$)
        - Inline math: $formula$ (e.g., The area is $A = \\pi r^2$)
        - Fractions: $\\frac{{numerator}}{{denominator}}$
        - Units: $\\text{{m/s}}^2$, $\\text{{kg}}$, $\\text{{N}}$, $\\text{{J}}$, etc.
        - This LaTeX formatting is MANDATORY for all mathematical expressions!
        """
        return ""
    
    def _build_hint_level_1(self, question_text: str, numerical_values: List[str], question_keywords: List[str], subject: str) -> str:
        """Build hint for level 1"""
        
        hint_elements = []
        
        if numerical_values:
            hint_elements.append(f"I notice the numbers {', '.join(numerical_values)} in this question")
        
        if question_keywords:
            hint_elements.append(f"The key concept here is about {', '.join(question_keywords)}")
        
        # Identify what type of question this is
        question_type = ""
        if any(word in question_text.lower() for word in ['what is', 'which is', 'what does']):
            question_type = "This is asking you to identify or define something"
        elif any(word in question_text.lower() for word in ['how', 'calculate', 'find']):
            question_type = "This requires you to work through a process or calculation"
        elif any(word in question_text.lower() for word in ['why', 'because', 'reason']):
            question_type = "This is asking you to explain reasoning or cause-effect"
        
        specific_focus = ""
        if subject == "Mathematics" and numerical_values:
            specific_focus = f"Focus on what operation you need to perform with these numbers: {', '.join(numerical_values)}"
        elif subject in ["Science", "Physical Science", "Physics"] and question_keywords:
            specific_focus = f"Think about how {question_keywords[0]} works in this context" if question_keywords else ""
        elif "percentage" in question_text.lower():
            specific_focus = "This is a percentage problem - think about the formula: $\\text{{percentage}} = \\frac{{\\text{{part}}}}{{\\text{{whole}}}} \\times 100\\%$"
        elif "area" in question_text.lower():
            specific_focus = "This is asking about area - remember the formula depends on the shape"
        
        return f"""
        Generate the FIRST hint for this question: "{question_text}"
        
        Start with: "👋 Hi! I'm your tutor for this question. Let me help you solve this step by step!
        
        🎯 My goal: Guide you through the solution without giving away the answer immediately.
        
        💭 How I work: I'll give you progressive hints and wait for your thoughts before the next hint.
        
        📝 First, let's analyze this question together:
        
        Your first hint should:
        1. Point out the specific elements: {hint_elements}
        2. {question_type}
        3. {specific_focus if specific_focus else 'Identify what the question is really asking'}
        4. Give them a specific starting point or approach
        5. Ask them what they think about these elements
        
        Make it engaging and specific to THIS question's content!"
        """
    
    def _build_hint_level_2(self, student_input: str, numerical_values: List[str], question_keywords: List[str]) -> str:
        """Build hint for level 2"""
        
        return f"""
        The student responded: "{student_input}"
        
        Now provide the SECOND progressive hint that:
        1. Acknowledges their response positively
        2. Guides them toward the correct method/approach for THIS specific question
        3. If it's a calculation: show them what formula or operation to use (with LaTeX formatting)
        4. If it's a concept: break down the concept as it applies here
        5. Give them a more specific direction without revealing the answer
        6. Use the actual content from the question (numbers: {numerical_values}, keywords: {question_keywords})
        7. Use proper LaTeX formatting for any mathematical expressions
        """
    
    def _build_hint_level_3(self, student_input: str, all_options: List[str], correct_answer: str) -> str:
        """Build hint for level 3"""
        
        return f"""
        The student responded: "{student_input}"
        
        Provide the THIRD progressive hint that:
        1. Builds on their understanding so far
        2. Shows partial working/steps for THIS question
        3. Eliminates 1-2 obviously wrong options from: {all_options}
        4. Gives them most of the solution process but lets them complete it
        5. If it's calculation: show the setup and maybe first step using LaTeX formatting
        6. Be very specific to this question's data and context
        7. Use LaTeX notation for any mathematical expressions: $formula$ or $formula$
        """
    
    def _build_hint_level_4_plus(self, student_input: str, question_text: str, correct_answer: str, explanation: str, topic: str, numerical_values: List[str]) -> str:
        """Build hint for level 4 and above (complete solution)"""
        
        return f"""
        The student has asked for more help. Provide the COMPLETE solution:
        
        1. Show the full step-by-step solution for this specific question
        2. Use the actual numbers and data from the question: {numerical_values}
        3. Explain WHY the correct answer is: {correct_answer}
        4. Show all calculation steps if it's a math problem using LaTeX formatting
        5. Explain the reasoning clearly
        6. Connect it back to the topic: {topic}
        7. End with encouragement about understanding the concept
        8. Use LaTeX notation for all mathematical expressions: $formula$ for display, $formula$ for inline
        
        Question: "{question_text}"
        Student response: "{student_input}"
        Explanation available: {explanation}
        
        Be comprehensive but still encouraging!
        """
    
    def _generate_fallback_hint(self, hint_level: int, question_text: str, correct_answer: str, explanation: str, topic: str, numerical_values: List[str], all_options: List[str], question_keywords: List[str]) -> str:
        """Generate fallback hints when API fails"""
        
        if hint_level == 1:
            fallback_hint = f"👋 Hi! I'm your tutor for this question.\n\n🎯 Let's look at this question: \"{question_text}\"\n\n"
            
            if numerical_values:
                fallback_hint += f"🔢 I notice there are numbers in this question: {', '.join(numerical_values)}. "
            
            if question_keywords:
                fallback_hint += f"📖 This question is about {', '.join(question_keywords)}. "
            
            if "calculate" in question_text.lower() or numerical_values:
                fallback_hint += "This looks like a calculation problem. What operation do you think we need to use? 🤔"
            elif "what is" in question_text.lower():
                fallback_hint += "This is asking you to identify something. Look at the options and think about which one best fits. 🤔"
            else:
                fallback_hint += "Think about what this question is really asking. What's the main concept being tested? 🤔"
                
            return fallback_hint
            
        elif hint_level == 2:
            return f"Good thinking! Now let's focus on the key part of this question. Looking at \"{question_text}\", what specific approach or method should we use? Think about the main concept of {topic}. 💡"
            
        elif hint_level == 3:
            wrong_options = [opt for opt in all_options if opt != correct_answer][:2] if all_options else []
            return f"Let me help you narrow it down! We can eliminate these options: {', '.join(wrong_options)} because they don't fit the question. Now focus on the remaining choices. What do you think? 🎯"
            
        else:
            return f"Here's the complete solution: The correct answer is {correct_answer}. {explanation if explanation else 'This relates to the key concepts of ' + topic + '.'} Now you can see how to approach similar questions! 🌟"
    
    def generate_comprehensive_feedback(self, student_data: Dict[str, Any]) -> str:
        """Generate comprehensive AI-powered feedback based on student learning patterns and mistakes"""
        
        # Extract data from session
        quiz_attempts = student_data.get('quiz_attempts', [])
        topics_studied = student_data.get('topics_studied', [])
        chat_interactions = student_data.get('chat_interactions', [])
        video_views = student_data.get('video_views', [])
        continuous_quiz_stats = student_data.get('continuous_quiz_stats', {})
        final_quiz_results = student_data.get('final_quiz_results', [])
        writing_quiz_evaluations = student_data.get('writing_quiz_evaluations', [])
        student_name = student_data.get('student_name', 'Student')
        current_topic = student_data.get('current_topic', 'General Learning')
        current_subject = student_data.get('current_subject', 'General')
        class_level = student_data.get('class_level', 'Class')
        
        # Calculate learning metrics
        total_study_time = len(topics_studied) * 15  # Assume 15 min per topic
        total_quizzes = len(quiz_attempts)
        avg_quiz_score = sum(q.get('score', 0) for q in quiz_attempts) / max(total_quizzes, 1)
        total_chat_questions = len(chat_interactions)
        videos_watched = len(video_views)
        
        # Analyze quiz performance patterns
        if quiz_attempts:
            recent_scores = [q.get('score', 0) for q in quiz_attempts[-5:]]
            early_scores = [q.get('score', 0) for q in quiz_attempts[:5]] if len(quiz_attempts) > 5 else []
            improvement_trend = "stable"
            if early_scores and recent_scores:
                early_avg = sum(early_scores) / len(early_scores)
                recent_avg = sum(recent_scores) / len(recent_scores)
                if recent_avg > early_avg + 10:
                    improvement_trend = "improving"
                elif recent_avg < early_avg - 10:
                    improvement_trend = "declining"
        else:
            improvement_trend = "no_data"
        
        # Analyze mistake patterns from continuous quiz
        mistake_patterns = []
        if continuous_quiz_stats:
            consecutive_wrong = continuous_quiz_stats.get('consecutive_wrong', 0)
            last_wrong_concept = continuous_quiz_stats.get('last_wrong_concept', '')
            total_questions = continuous_quiz_stats.get('total_questions', 0)
            correct_answers = continuous_quiz_stats.get('correct_answers', 0)
            
            if consecutive_wrong > 0:
                mistake_patterns.append(f"Recent difficulty with {last_wrong_concept}")
            if total_questions > 0:
                accuracy = (correct_answers / total_questions) * 100
                if accuracy < 60:
                    mistake_patterns.append("Low quiz accuracy")
                elif accuracy > 80:
                    mistake_patterns.append("High quiz accuracy")
        
        # Analyze subject-wise performance
        subject_performance = {}
        for quiz in quiz_attempts:
            topic = quiz.get('topic', 'Unknown')
            score = quiz.get('score', 0)
            if topic not in subject_performance:
                subject_performance[topic] = []
            subject_performance[topic].append(score)
        
        # Find strongest and weakest topics
        topic_averages = {topic: sum(scores)/len(scores) for topic, scores in subject_performance.items() if scores}
        strongest_topics = sorted(topic_averages.items(), key=lambda x: x[1], reverse=True)[:3]
        weakest_topics = sorted(topic_averages.items(), key=lambda x: x[1])[:3]
        
        # Analyze learning behavior patterns
        learning_patterns = []
        if total_chat_questions > 10:
            learning_patterns.append("High engagement with AI assistant")
        elif total_chat_questions < 3:
            learning_patterns.append("Limited use of interactive help")
        
        if videos_watched > 5:
            learning_patterns.append("Active video learner")
        elif videos_watched < 2:
            learning_patterns.append("Prefers text-based learning")
        
        if total_quizzes > 8:
            learning_patterns.append("Quiz-focused learner")
        
        # Analyze study consistency
        if topics_studied:
            study_dates = [t.get('date', '') for t in topics_studied if t.get('date')]
            unique_dates = len(set(study_dates))
            if unique_dates > 5:
                learning_patterns.append("Consistent daily study habit")
            elif unique_dates < 3:
                learning_patterns.append("Irregular study pattern")
        
        system_prompt = f"""
        You are an experienced educational counselor and learning analytics expert specializing in AP State Board curriculum.
        Analyze the provided student learning data and generate comprehensive, realistic feedback that:
        
        1. ACKNOWLEDGES the student's specific achievements and efforts
        2. IDENTIFIES genuine patterns in their learning behavior and mistakes
        3. PROVIDES actionable, personalized recommendations
        4. MOTIVATES the student while being honest about areas needing improvement
        5. CONNECTS feedback to AP State Board learning objectives for {class_level}
        
        TONE AND STYLE:
        - Warm, encouraging, and supportive
        - Professional yet friendly
        - Specific and data-driven, not generic
        - Realistic and honest
        - Age-appropriate for {class_level} students
        
        FEEDBACK STRUCTURE:
        Use emojis and clear sections for better readability:
        1. 🎯 **Learning Overview & Achievements**
        2. 📊 **Performance Analysis** 
        3. 🔍 **Areas for Growth**
        4. 💡 **Personalized Recommendations**
        5. 🚀 **Next Steps & Goals**
        6. 🌟 **Motivational Message**
        """
        
        human_prompt = f"""
        Generate comprehensive feedback for {student_name}, a {class_level} student studying {current_subject}.
        
        📚 LEARNING ACTIVITY DATA:
        - Current Topic: {current_topic}
        - Topics Studied: {len(topics_studied)} topics
        - Total Study Time: ~{total_study_time} minutes
        - Quizzes Taken: {total_quizzes}
        - Average Quiz Score: {avg_quiz_score:.1f}%
        - Chat Questions Asked: {total_chat_questions}
        - Videos Watched: {videos_watched}
        
        📈 PERFORMANCE TRENDS:
        - Learning Trend: {improvement_trend}
        - Quiz Accuracy: {continuous_quiz_stats.get('correct_answers', 0)}/{continuous_quiz_stats.get('total_questions', 0)} correct
        - Recent Mistakes: {mistake_patterns if mistake_patterns else ['No significant patterns detected']}
        
        🏆 STRONGEST TOPICS:
        {chr(10).join([f"- {topic}: {score:.1f}% average" for topic, score in strongest_topics]) if strongest_topics else "- Still building expertise"}
        
        📚 TOPICS NEEDING ATTENTION:
        {chr(10).join([f"- {topic}: {score:.1f}% average" for topic, score in weakest_topics]) if weakest_topics else "- Maintaining consistent performance"}
        
        🎯 LEARNING BEHAVIOR PATTERNS:
        {chr(10).join([f"- {pattern}" for pattern in learning_patterns]) if learning_patterns else "- Developing learning routine"}
        
        📝 WRITING QUIZ PERFORMANCE:
        - Writing Evaluations: {len(writing_quiz_evaluations)} completed
        
        💭 INTERACTION STYLE:
        - Questions Asked: {total_chat_questions} (Shows curiosity level)
        - Help-Seeking: {'Active' if total_chat_questions > 5 else 'Moderate' if total_chat_questions > 2 else 'Limited'}
        
        REQUIREMENTS:
        1. Be SPECIFIC to this student's actual data - don't use generic statements
        2. Reference the actual numbers and patterns shown above
        3. Provide realistic, achievable goals based on current performance
        4. Include specific study strategies for {current_subject} and {current_topic}
        5. Address any concerning patterns (like declining scores or low engagement)
        6. Celebrate genuine achievements and progress
        7. Give practical next steps they can implement immediately
        8. Connect recommendations to AP State Board learning standards
        9. Be encouraging but honest about areas needing work
        10. Make the feedback feel personal and meaningful to {student_name}
        
        Make this feedback feel like it comes from an experienced teacher who truly understands this student's learning journey.
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            # Provide a fallback feedback based on available data
            return self._generate_fallback_feedback(student_data, student_name, total_quizzes, avg_quiz_score, 
                                                  total_chat_questions, videos_watched, improvement_trend)
    
    def _generate_fallback_feedback(self, student_data: Dict, student_name: str, total_quizzes: int, 
                                  avg_quiz_score: float, total_chat_questions: int, videos_watched: int, 
                                  improvement_trend: str) -> str:
        """Generate fallback feedback when AI is unavailable"""
        
        feedback = f"# 📊 Learning Progress Report for {student_name}\n\n"
        
        # Learning Overview
        feedback += "## 🎯 **Learning Overview & Achievements**\n"
        feedback += f"Great work, {student_name}! You've been actively engaged in your learning journey. "
        
        if total_quizzes > 5:
            feedback += f"You've completed {total_quizzes} quizzes, showing dedication to testing your knowledge. "
        if videos_watched > 3:
            feedback += f"You've watched {videos_watched} educational videos, demonstrating varied learning approaches. "
        if total_chat_questions > 5:
            feedback += f"You've asked {total_chat_questions} questions, showing curiosity and engagement. "
        
        feedback += "\n\n"
        
        # Performance Analysis
        feedback += "## 📊 **Performance Analysis**\n"
        if avg_quiz_score > 75:
            feedback += f"🌟 Excellent! Your average quiz score of {avg_quiz_score:.1f}% shows strong understanding. "
        elif avg_quiz_score > 60:
            feedback += f"👍 Good progress! Your average quiz score of {avg_quiz_score:.1f}% shows you're on the right track. "
        else:
            feedback += f"📚 Your average quiz score of {avg_quiz_score:.1f}% indicates opportunities for improvement. "
        
        if improvement_trend == "improving":
            feedback += "📈 Your scores show an upward trend - keep up the excellent work!\n"
        elif improvement_trend == "declining":
            feedback += "📉 Your recent scores suggest you might need to review some concepts.\n"
        else:
            feedback += "📊 Your performance has been consistent.\n"
        
        feedback += "\n"
        
        # Areas for Growth
        feedback += "## 🔍 **Areas for Growth**\n"
        if avg_quiz_score < 70:
            feedback += "• Focus on understanding core concepts before moving to advanced topics\n"
            feedback += "• Take more time to review explanations after each quiz\n"
        if total_chat_questions < 3:
            feedback += "• Don't hesitate to ask more questions when you're unsure\n"
        if videos_watched < 2:
            feedback += "• Try incorporating video learning for better understanding\n"
        
        feedback += "\n"
        
        # Recommendations
        feedback += "## 💡 **Personalized Recommendations**\n"
        feedback += "• Create a regular study schedule with daily practice\n"
        feedback += "• Use the interactive Q&A feature more frequently\n"
        feedback += "• Review topics where you scored below 70%\n"
        feedback += "• Try different learning methods (videos, explanations, quizzes)\n\n"
        
        # Motivational message
        feedback += "## 🌟 **Keep Going!**\n"
        feedback += f"Remember, {student_name}, learning is a journey, not a destination. Every question you ask and every quiz you take brings you closer to mastery. Stay curious, stay committed, and celebrate your progress along the way! 🚀"
        
        return feedback