import streamlit as st
import sqlite3

# Connect to the database
conn = sqlite3.connect('personality_scores.db')
c = conn.cursor()

# Create the table with all necessary columns if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS user_scores (
        user_id TEXT PRIMARY KEY,
        extroversion REAL,
        agreeableness REAL,
        conscientiousness REAL,
        neuroticism REAL,
        openness REAL,
        learning_style TEXT,
        interests TEXT,
        motivation TEXT,
        academic_levels TEXT
    )
''')

conn.commit()

# Streamlit App
st.title("Student Profile Assessment")
st.write("Please answer the following questions to help us understand you better.")


# Personality questions
questions = {
    "I am someone who is talkative.": "Extroversion",
    "I tend to find fault with others.": "Agreeableness",
    "I do a thorough job.": "Conscientiousness",
    "I get nervous easily.": "Neuroticism",
    "I have an active imagination.": "Openness"
}

# Additional questions
st.subheader("Learning Style")
learning_style = st.radio(
    "How do you prefer to learn?",
    ('Visual', 'Auditory', 'Reading/Writing', 'Kinesthetic')
)

st.subheader("Interests")
interests = st.multiselect(
    "Select your interests:",
    ['Mathematics', 'Science', 'Literature', 'History', 'Arts', 'Technology']
)

st.subheader("Motivation")
motivation = st.text_area("What motivates you to learn?")

st.subheader("Academic Levels")
subjects = ['Mathematics', 'Science', 'Literature', 'History', 'Arts', 'Technology']
academic_levels = {subject: st.slider(f"Rate your proficiency in {subject}:", 1, 5, 3) for subject in subjects}

# Collecting responses
responses = {}
scores = {"Strongly disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4, "Strongly agree": 5}
for question, trait in questions.items():
    response = st.radio(question, ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree'], key=question)
    responses[trait] = responses.get(trait, []) + [response]

# User ID Input
user_id = st.text_input("Enter your user ID or email")

# Calculate trait scores
trait_scores = {}
for trait, response_list in responses.items():
    total_score = sum(scores[response] for response in response_list)
    average_score = total_score / len(response_list) if response_list else 0
    trait_scores[trait] = average_score

if st.button('Submit'):
    if user_id:
        # Insert or update scores in the database
        c.execute('''INSERT OR REPLACE INTO user_scores 
                     (user_id, extroversion, agreeableness, conscientiousness, neuroticism, openness, learning_style, interests, motivation, academic_levels)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (user_id, trait_scores.get('Extroversion', 0), trait_scores.get('Agreeableness', 0), 
                   trait_scores.get('Conscientiousness', 0), trait_scores.get('Neuroticism', 0), 
                   trait_scores.get('Openness', 0), learning_style, ', '.join(interests), motivation,
                   ', '.join([f"{subject}: {level}" for subject, level in academic_levels.items()])))

        conn.commit()
        st.write("Thank you for completing the assessment! Your responses have been saved.")
    else:
        st.write("Please enter your user ID or email.")

conn.close()
