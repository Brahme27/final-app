import streamlit as st
from typing import Dict

def learning_preferences_survey():
    st.title("🎯 Learning Preferences Survey")
    st.write("Help us personalize your learning experience!")
    
    # Initialize session state
    if 'survey_data' not in st.session_state:
        st.session_state.survey_data = {}
    
    with st.form("learning_preferences"):
        # Question 1: Activities - Multiple selection with checkboxes
        st.subheader("1. What activities make you lose track of time?")
        st.caption("Select all that apply")
        
        activities = [
            "Playing sports or exercising",
            "Drawing, painting, or creating art", 
            "Playing video games",
            "Reading books or stories",
            "Watching movies/TV shows",
            "Listening to or making music",
            "Building or fixing things",
            "Cooking or baking",
            "Being outdoors in nature",
            "Hanging out with friends",
            "Learning about science/technology",
            "Solving puzzles or brain teasers",
            "Writing or journaling",
            "Shopping or fashion"
        ]
        
        # Use columns for better layout
        cols = st.columns(2)
        selected_activities = []
        
        for i, activity in enumerate(activities):
            col = cols[i % 2]
            if col.checkbox(activity, key=f"activity_{i}"):
                selected_activities.append(activity)
        
        # Question 2: Storytelling styles - Multiple selection
        st.subheader("2. What storytelling styles do you enjoy most?")
        st.caption("Select all that apply")
        
        storytelling_styles = [
            "Action-packed adventures",
            "Funny and humorous content",
            "Mystery and detective stories", 
            "Fantasy and magical worlds",
            "Sci-fi and futuristic concepts",
            "Real-life stories and biographies",
            "Horror and thrilling content",
            "Romantic storylines",
            "Historical events and periods",
            "Documentary-style factual content"
        ]
        
        selected_styles = st.multiselect(
            "Choose your preferred styles:",
            storytelling_styles,
            key="storytelling_styles"
        )
        
        # Question 3: Memory techniques - Multiple selection with limit
        st.subheader("3. What makes a lesson stick in your memory?")
        st.caption("Select your top 3 choices")
        
        memory_techniques = [
            "Real-world examples I can relate to",
            "Stories and personal anecdotes",
            "Step-by-step visual breakdowns", 
            "Interactive examples I can imagine doing",
            "Connections to current events or trends",
            "Comparisons to things I already know",
            "Surprising facts or 'mind-blowing' moments",
            "Practical applications I can use immediately",
            "Debates or different perspectives on topics",
            "Challenges that make me think critically"
        ]
        
        selected_memory = st.multiselect(
            "Choose up to 3 options:",
            memory_techniques,
            key="memory_techniques",
            max_selections=3
        )
        
        # Question 4: Learning approach - Single selection
        st.subheader("4. When learning something new, which approach works best for you?")
        
        learning_approaches = [
            "Show me with detailed descriptions and imagery",
            "Explain it step-by-step with clear reasoning",
            "Give me examples I can work through mentally", 
            "Let me read comprehensive explanations and take notes",
            "Combine all approaches for complete understanding"
        ]
        
        selected_approach = st.radio(
            "Choose one:",
            learning_approaches,
            key="learning_approach"
        )
        
        # Question 5: Difficulty preference - Single selection  
        st.subheader("5. How do you prefer difficult topics to be explained?")
        
        difficulty_preferences = [
            "Quick overview first, then dive into details if I'm interested",
            "Start simple and gradually build up complexity",
            "Give me the big picture, then break it down into parts",
            "Show me multiple examples before explaining the concept", 
            "Break it into small, manageable chunks with frequent check-ins",
            "Provide a comprehensive deep-dive all at once",
            "Let me choose the depth level as I go"
        ]
        
        selected_difficulty = st.selectbox(
            "Choose your preference:",
            difficulty_preferences,
            key="difficulty_preference"
        )
        
        # Submit button
        submitted = st.form_submit_button("Save My Preferences", type="primary")
        
        if submitted:
            # Store results in session state
            st.session_state.survey_data = {
                "activities": selected_activities,
                "storytelling_styles": selected_styles,
                "memory_techniques": selected_memory,
                "learning_approach": selected_approach,
                "difficulty_preference": selected_difficulty
            }
            
            st.success("✅ Preferences saved successfully!")
            st.balloons()
            
            # Show summary
            with st.expander("📋 Your Learning Profile Summary", expanded=True):
                if selected_activities:
                    st.write("**Favorite Activities:**", ", ".join(selected_activities))
                if selected_styles:
                    st.write("**Preferred Storytelling:**", ", ".join(selected_styles))
                if selected_memory:
                    st.write("**Memory Boosters:**", ", ".join(selected_memory))
                st.write("**Learning Style:**", selected_approach)
                st.write("**Difficulty Preference:**", selected_difficulty)
    
    # Optional: Add a reset button outside the form
    if st.button("🔄 Reset Survey", type="secondary"):
        st.session_state.survey_data = {}
        st.rerun()

# Additional utility functions
def get_user_preferences():
    """Get stored user preferences"""
    return st.session_state.get('survey_data', {})

def create_user_profile_summary():
    """Create a text summary of user preferences for AI personalization"""
    preferences = get_user_preferences()
    
    if not preferences:
        return "No preferences set yet."
    
    summary = "User Learning Profile:\n"
    
    if preferences.get('activities'):
        summary += f"- Enjoys: {', '.join(preferences['activities'])}\n"
    
    if preferences.get('storytelling_styles'):
        summary += f"- Prefers content style: {', '.join(preferences['storytelling_styles'])}\n"
    
    if preferences.get('memory_techniques'):
        summary += f"- Learns best through: {', '.join(preferences['memory_techniques'])}\n"
    
    if preferences.get('learning_approach'):
        summary += f"- Learning approach: {preferences['learning_approach']}\n"
    
    if preferences.get('difficulty_preference'):
        summary += f"- Difficulty handling: {preferences['difficulty_preference']}\n"
    
    return summary

# Main app usage example
if __name__ == "__main__":
    # Page config
    st.set_page_config(
        page_title="Learning Preferences Survey",
        page_icon="🎯",
        layout="wide"
    )
    
    # Run the survey
    learning_preferences_survey()
    
    # Show current preferences (for testing)
    if st.session_state.get('survey_data'):
        st.sidebar.header("Current Profile")
        st.sidebar.text(create_user_profile_summary())