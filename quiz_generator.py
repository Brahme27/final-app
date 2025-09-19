"""
Quiz Generator Module
Generates adaptive and final quizzes using AI
Enhanced with continuous adaptive questioning
"""

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
import random
from typing import Dict, List, Any

class QuizGenerator:
    def __init__(self, api_key: str):
        """Initialize Quiz Generator with OpenAI API key"""
        self.api_key = api_key
        self.llm = ChatOpenAI(
            api_key=api_key,
            model="gpt-4o-mini",
            temperature=0.5,
            max_tokens=2000
        )
    
    def _randomize_answer_options(self, correct_answer_text: str, wrong_options: List[str]) -> Dict[str, str]:
        """
        Randomize the position of the correct answer among options
        Returns a dict with 'options' list and 'correct_answer' string
        """
        # Create list of all answer texts (without A), B), C), D) prefixes)
        all_answers = [correct_answer_text] + wrong_options
        
        # Shuffle the answers
        random.shuffle(all_answers)
        
        # Add A), B), C), D) prefixes
        option_labels = ['A)', 'B)', 'C)', 'D)']
        formatted_options = [f"{label} {answer}" for label, answer in zip(option_labels, all_answers)]
        
        # Find which option now contains the correct answer
        correct_option = None
        for option in formatted_options:
            if correct_answer_text in option:
                correct_option = option
                break
        
        return {
            'options': formatted_options,
            'correct_answer': correct_option
        }
    
    def _randomize_existing_question(self, question_data: Dict) -> Dict:
        """
        Randomize an existing question's answer positions
        Useful for AI-generated questions that might have predictable answer positions
        """
        if not question_data or 'options' not in question_data or 'correct_answer' not in question_data:
            return question_data
        
        try:
            # Extract the answer texts without A), B), C), D) prefixes
            answer_texts = []
            correct_text = None
            
            for option in question_data['options']:
                # Remove A), B), C), D) prefix
                clean_text = option[3:].strip() if len(option) > 3 else option
                answer_texts.append(clean_text)
                
                # Check if this is the correct answer
                if option == question_data['correct_answer']:
                    correct_text = clean_text
            
            if correct_text and len(answer_texts) >= 2:
                # Remove correct answer from list and create wrong options
                wrong_options = [text for text in answer_texts if text != correct_text]
                
                # Randomize using our existing method
                randomized = self._randomize_answer_options(correct_text, wrong_options)
                
                # Update the question data
                question_data['options'] = randomized['options']
                question_data['correct_answer'] = randomized['correct_answer']
            
            return question_data
            
        except Exception as e:
            # If randomization fails, return original question
            print(f"Failed to randomize question: {e}")
            return question_data
    
    def generate_next_adaptive_question(self, topic: str, subject: str, class_level: str, 
                                      difficulty: str = "easy", previous_wrong_answer: str = None,
                                      question_history: List[str] = None) -> Dict:
        """Generate the next adaptive question based on performance"""
        
        # Ensure question_history is a list
        if question_history is None:
            question_history = []
        
        system_prompt = f"""
        You are an expert adaptive quiz creator for {class_level} students studying {subject}.
        Create 1 multiple-choice question about "{topic}" with {difficulty} difficulty level.
        
        IMPORTANT ADAPTIVE RULES:
        - If student got previous question wrong, create a RELATED but DIFFERENT question on the same concept
        - If student is doing well, gradually increase difficulty
        - Focus on the specific area where student struggled
        - Never repeat the exact same question
        
        Difficulty Guidelines:
        - Easy: Basic recall and understanding questions
        - Medium: Application and analysis questions  
        - Hard: Synthesis and evaluation questions
        
        Format your response as a valid JSON object with this exact structure:
        {{
            "question": "Question text here?",
            "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
            "correct_answer": "A) Option 1",
            "explanation": "Brief explanation of why this is correct and how it relates to the concept",
            "concept_focus": "The specific concept this question tests",
            "difficulty": "{difficulty}"
        }}
        
        Requirements:
        1. Questions must be appropriate for {class_level} students
        2. Use clear, simple language
        3. Make sure only one option is clearly correct
        4. Include realistic distractors
        5. If previous answer was wrong, focus on that concept area
        6. Never repeat questions from history
        """
        
        human_prompt = f"""
        Create 1 {difficulty} difficulty adaptive question about "{topic}" for {class_level} students studying {subject}.
        
        Context:
        - Topic: {topic}
        - Subject: {subject}
        - Class Level: {class_level}
        - Current Difficulty: {difficulty}
        """
        
        # Add context about previous wrong answer
        if previous_wrong_answer:
            human_prompt += f"\n- Previous Wrong Answer: The student struggled with: {previous_wrong_answer}"
            human_prompt += "\n- Focus on the same concept but ask it differently to reinforce learning"
        
        # Add question history to avoid repeats
        if question_history:
            human_prompt += f"\n- Previous Questions Asked: {', '.join(question_history[-5:])}"  # Last 5 questions
            human_prompt += "\n- Make sure this question is different from previous ones"
        
        human_prompt += "\n\nReturn only the JSON object, no additional text."
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Try to parse JSON response
            try:
                question_data = json.loads(response.content)
                # Validate required fields
                if self._validate_question_data(question_data):
                    # Randomize the answer positions for AI-generated questions
                    randomized_question = self._randomize_existing_question(question_data)
                    return randomized_question
                else:
                    return self._create_fallback_adaptive_question(topic, subject, class_level, difficulty)
            except json.JSONDecodeError:
                return self._create_fallback_adaptive_question(topic, subject, class_level, difficulty)
                
        except Exception as e:
            print(f"Error generating adaptive question: {e}")
            return self._create_fallback_adaptive_question(topic, subject, class_level, difficulty)
    
    def _validate_question_data(self, question_data: Dict) -> bool:
        """Validate question data structure"""
        required_fields = ['question', 'options', 'correct_answer', 'explanation']
        
        if not all(field in question_data for field in required_fields):
            return False
        
        if not isinstance(question_data['options'], list) or len(question_data['options']) != 4:
            return False
        
        if question_data['correct_answer'] not in question_data['options']:
            return False
        
        return True
    
    def _create_fallback_adaptive_question(self, topic: str, subject: str, class_level: str, difficulty: str) -> Dict:
        """Create fallback question when AI generation fails"""
        
        question_templates = {
            "Mathematics": {
                "easy": f"What is a basic concept in {topic}?",
                "medium": f"How do you apply {topic} in problem solving?",
                "hard": f"What is an advanced application of {topic}?"
            },
            "Science": {
                "easy": f"What is {topic}?",
                "medium": f"How does {topic} work in nature?", 
                "hard": f"What are the complex aspects of {topic}?"
            },
            "Environmental Studies": {
                "easy": f"What do we learn about {topic}?",
                "medium": f"How does {topic} affect our environment?",
                "hard": f"What are the broader implications of {topic}?"
            }
        }
        
        # Get template based on subject and difficulty
        templates = question_templates.get(subject, question_templates["Science"])
        question_text = templates.get(difficulty, templates["easy"])
        
        # Create randomized options
        correct_answer_text = f"Basic concept of {topic}"
        wrong_options = [
            f"Advanced concept of {topic}",
            f"Related concept to {topic}",
            f"All concepts are important"
        ]
        
        randomized = self._randomize_answer_options(correct_answer_text, wrong_options)
        
        return {
            "question": question_text,
            "options": randomized['options'],
            "correct_answer": randomized['correct_answer'],
            "explanation": f"This relates to understanding the fundamental concepts of {topic}.",
            "concept_focus": f"Basic understanding of {topic}",
            "difficulty": difficulty
        }
    
    def determine_next_difficulty(self, current_difficulty: str, is_correct: bool, consecutive_correct: int, consecutive_wrong: int) -> str:
        """Determine next question difficulty based on performance"""
        
        if consecutive_wrong >= 2:
            # If student got 2+ wrong in a row, make it easier or stay same level
            if current_difficulty == "hard":
                return "medium"
            elif current_difficulty == "medium":
                return "easy"
            else:
                return "easy"  # Stay at easy level
        
        elif consecutive_correct >= 2:
            # If student got 2+ correct in a row, increase difficulty
            if current_difficulty == "easy":
                return "medium"
            elif current_difficulty == "medium":
                return "hard"
            else:
                return "hard"  # Stay at hard level
        
        else:
            # Keep current difficulty if performance is mixed
            return current_difficulty
    
    def generate_adaptive_quiz(self, topic: str, subject: str, class_level: str, 
                             difficulty: str = "easy", num_questions: int = 3) -> List[Dict]:
        """Generate adaptive quiz questions based on difficulty level (Legacy method for compatibility)"""
        
        questions = []
        for i in range(num_questions):
            question = self.generate_next_adaptive_question(topic, subject, class_level, difficulty)
            questions.append(question)
        
        return questions
    
    def generate_final_quiz(self, topic: str, subject: str, class_level: str) -> List[Dict]:
        """Generate a comprehensive 10-question final quiz"""
        
        system_prompt = f"""
        You are an expert educator creating a comprehensive final assessment for {class_level} students.
        Create 10 multiple-choice questions about "{topic}" in {subject} that test complete understanding.
        
        Question Distribution:
        - 4 Easy questions (basic concepts and recall)
        - 4 Medium questions (application and analysis)
        - 2 Hard questions (synthesis and critical thinking)
        
        Format your response as a valid JSON array with this exact structure:
        [
            {{
                "question": "Question text here?",
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "correct_answer": "A) Option 1",
                "explanation": "Brief explanation of why this is correct",
                "difficulty": "easy"
            }}
        ]
        
        Requirements:
        1. Cover different aspects of the topic
        2. Use age-appropriate language for {class_level}
        3. No repeated questions or concepts
        4. Clear, unambiguous correct answers
        5. Good distractors that test understanding
        6. Progressive difficulty throughout the quiz
        """
        
        human_prompt = f"""
        Create a comprehensive 10-question final quiz about "{topic}" for {class_level} students studying {subject}.
        
        The quiz should:
        - Test complete understanding of the topic
        - Include questions of varying difficulty
        - Cover all major concepts within the topic
        - Be fair and appropriate for the grade level
        
        Topic: {topic}
        Subject: {subject}
        Class Level: {class_level}
        
        Return only the JSON array with exactly 10 questions, no additional text.
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Try to parse JSON response
            try:
                questions = json.loads(response.content)
                # Validate the questions
                validated_questions = self.validate_quiz_questions(questions)
                
                # Randomize answer positions for all validated questions
                randomized_questions = []
                for question in validated_questions:
                    randomized_question = self._randomize_existing_question(question)
                    randomized_questions.append(randomized_question)
                
                # If we have at least some valid questions, use them and generate the rest individually
                if len(randomized_questions) > 0:
                    # Use valid questions and generate remaining ones individually
                    remaining_needed = 10 - len(randomized_questions)
                    if remaining_needed > 0:
                        # Generate remaining questions individually using adaptive method
                        for i in range(remaining_needed):
                            difficulty = "easy" if i < 4 else "medium" if i < 8 else "hard"
                            individual_question = self.generate_next_adaptive_question(
                                topic, subject, class_level, difficulty
                            )
                            randomized_questions.append(individual_question)
                    
                    return randomized_questions[:10]  # Ensure exactly 10 questions
                else:
                    # If no valid questions, generate all individually
                    return self._generate_individual_final_questions(topic, subject, class_level)
                    
            except json.JSONDecodeError:
                # If JSON parsing fails, generate questions individually
                return self._generate_individual_final_questions(topic, subject, class_level)
                
        except Exception as e:
            print(f"Error generating final quiz: {e}")
            return self._generate_individual_final_questions(topic, subject, class_level)
    
    def _generate_individual_final_questions(self, topic: str, subject: str, class_level: str) -> List[Dict]:
        """Generate final quiz questions individually when batch generation fails"""
        questions = []
        
        # Generate 10 questions with varied difficulty
        difficulties = ["easy"] * 4 + ["medium"] * 4 + ["hard"] * 2
        
        for i, difficulty in enumerate(difficulties):
            try:
                question = self.generate_next_adaptive_question(
                    topic, subject, class_level, difficulty, 
                    question_history=[q.get("question", "") for q in questions]
                )
                questions.append(question)
            except Exception as e:
                print(f"Error generating individual question {i+1}: {e}")
                # Only use fallback for this specific question
                fallback_question = self._create_single_fallback_question(topic, subject, class_level, difficulty, i+1)
                questions.append(fallback_question)
        
        return questions
    
    def _create_single_fallback_question(self, topic: str, subject: str, class_level: str, difficulty: str, question_num: int) -> Dict:
        """Create a single fallback question with better content than generic template"""
        
        # Better subject-specific templates
        question_templates = {
            "Mathematics": {
                "easy": f"What is the basic principle of {topic}?",
                "medium": f"How would you solve a problem involving {topic}?",
                "hard": f"What is the most complex aspect of {topic}?"
            },
            "Science": {
                "easy": f"What is {topic}?",
                "medium": f"How does {topic} work in real life?", 
                "hard": f"What are the advanced applications of {topic}?"
            },
            "Environmental Studies": {
                "easy": f"Why is {topic} important for our environment?",
                "medium": f"How does {topic} impact our daily lives?",
                "hard": f"What are the long-term effects of {topic}?"
            },
            "English": {
                "easy": f"What is the main idea of {topic}?",
                "medium": f"How can we analyze {topic}?",
                "hard": f"What is the deeper meaning of {topic}?"
            },
            "Social Studies": {
                "easy": f"What is {topic} in history?",
                "medium": f"How did {topic} influence society?",
                "hard": f"What are the lasting impacts of {topic}?"
            }
        }
        
        # Get appropriate template
        templates = question_templates.get(subject, question_templates["Science"])
        question_text = templates.get(difficulty, templates["easy"])
        
        # Create subject-appropriate options
        if subject == "Mathematics":
            correct_answer_text = "It involves calculations and formulas"
            wrong_options = [
                "It's only theoretical",
                "It has no practical use",
                "It's too complex to understand"
            ]
        elif subject == "Science":
            correct_answer_text = "It's a natural phenomenon or concept"
            wrong_options = [
                "It's just a theory",
                "It doesn't affect us",
                "It's not important"
            ]
        elif subject == "Environmental Studies":
            correct_answer_text = "It helps us understand nature better"
            wrong_options = [
                "It's not relevant today",
                "It only affects animals",
                "It's too complicated"
            ]
        else:
            correct_answer_text = "It's an important concept to understand"
            wrong_options = [
                "It's not necessary to learn",
                "It's too difficult",
                "It has no meaning"
            ]
        
        # Randomize the answer options
        randomized = self._randomize_answer_options(correct_answer_text, wrong_options)
        
        return {
            "question": question_text,
            "options": randomized['options'],
            "correct_answer": randomized['correct_answer'],
            "explanation": f"Understanding {topic} is fundamental to learning {subject} at the {class_level} level.",
            "concept_focus": f"Understanding of {topic}",
            "difficulty": difficulty
        }
    
    def _create_fallback_questions(self, topic: str, subject: str, class_level: str, 
                                 difficulty: str, num_questions: int) -> List[Dict]:
        """Create fallback questions when AI generation fails"""
        
        # Generic question templates based on subject
        templates = {
            "Mathematics": [
                {
                    "question": f"What is the main concept in {topic}?",
                    "correct_answer_text": "Addition",
                    "wrong_options": ["Subtraction", "Multiplication", "Division"],
                    "explanation": "This is a basic concept question."
                }
            ],
            "Science": [
                {
                    "question": f"Which of the following is related to {topic}?",
                    "correct_answer_text": "Plants",
                    "wrong_options": ["Animals", "Water", "Air"],
                    "explanation": "This relates to the topic being studied."
                }
            ],
            "Environmental Studies": [
                {
                    "question": f"What can we learn from {topic}?",
                    "correct_answer_text": "All of the above",
                    "wrong_options": ["Conservation", "Pollution", "Resources"],
                    "explanation": "Environmental studies covers many interconnected topics."
                }
            ]
        }
        
        # Use generic template or create simple questions
        fallback_questions = []
        base_template = templates.get(subject, templates["Science"])
        
        for i in range(num_questions):
            # Create randomized options for each question
            correct_answer_text = f"Concept {i+1}"
            wrong_options = [
                f"Concept {i+2}",
                f"Concept {i+3}",
                f"All of the above"
            ]
            
            randomized = self._randomize_answer_options(correct_answer_text, wrong_options)
            
            question = {
                "question": f"Question {i+1}: What is an important aspect of {topic}?",
                "options": randomized['options'],
                "correct_answer": randomized['correct_answer'],
                "explanation": f"This is related to understanding {topic}.",
                "difficulty": difficulty
            }
            fallback_questions.append(question)
        
        return fallback_questions
    
    def validate_quiz_questions(self, questions: List[Dict]) -> List[Dict]:
        """Validate and clean quiz questions"""
        validated_questions = []
        
        for q in questions:
            # Ensure required fields exist
            if all(key in q for key in ['question', 'options', 'correct_answer']):
                # Ensure options is a list with 4 items
                if isinstance(q['options'], list) and len(q['options']) == 4:
                    # Ensure correct_answer is in options
                    if q['correct_answer'] in q['options']:
                        validated_questions.append(q)
        
        return validated_questions
    
    def shuffle_questions(self, questions: List[Dict]) -> List[Dict]:
        """Shuffle the order of questions"""
        shuffled = questions.copy()
        random.shuffle(shuffled)
        return shuffled
    
    def get_question_feedback(self, question: Dict, selected_answer: str) -> str:
        """Generate feedback for a quiz question"""
        is_correct = selected_answer == question['correct_answer']
        
        if is_correct:
            feedback = f"🎉 Correct! {question.get('explanation', 'Well done!')}"
        else:
            feedback = f"❌ Incorrect. The correct answer is {question['correct_answer']}. "
            feedback += question.get('explanation', 'Keep studying and try again!')
        
        return feedback