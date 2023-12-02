import os
import streamlit as st
import sqlite3
import openai
from config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_API_ENVIRONMENT
from constants import PINECONE_INDEX_NAME
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.schema import SystemMessage
import pinecone

# Set API key for OpenAI and Pinecone
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENVIRONMENT)

# Function to retrieve additional student profile data from the database
def get_student_profile(user_id):
    conn = sqlite3.connect('personality_scores.db')
    c = conn.cursor()
    c.execute("SELECT * FROM user_scores WHERE user_id = ?", (user_id,))
    profile = c.fetchone()
    conn.close()
    return profile

# Function to generate a comprehensive description using OpenAI
def generate_profile_description(profile):
    # Construct a summary of the profile
    profile_summary = f"Extroversion: {profile[1]}, Agreeableness: {profile[2]}, Conscientiousness: {profile[3]}, Neuroticism: {profile[4]}, Openness: {profile[5]}, Learning Style: {profile[6]}, Interests: {profile[7]}, Motivation: {profile[8]}, Academic Levels: {profile[9]}."
    prompt = f"Based on the following student profile, describe how to tailor the tutoring approach in a few words: {profile_summary}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()

# Streamlit App
st.title('Niels Brock Tutor')
usr_input = st.text_input('What is your question?')
user_id = st.text_input('Enter your user ID or email')

# Set OpenAI embeddings
embeddings = OpenAIEmbeddings(client='')

# Set Pinecone index
docsearch = Pinecone.from_existing_index(index_name=PINECONE_INDEX_NAME, embedding=embeddings)

# Check Streamlit input
if usr_input and user_id:
    # Retrieve student profile
    profile = get_student_profile(user_id)
    if profile:
        # Generate profile description
        profile_description = generate_profile_description(profile)

        # Create a system message to instruct the chatbot
        instruction_message = f"Personalize responses based on the student's profile: {profile_description}"

        # Initialize ChatOpenAI with the system message
        llm_chat = ChatOpenAI(temperature=0.9, max_tokens=700, model_name='gpt-4', client='')

        # Create SystemMessage with the instruction
        system_instruction = SystemMessage(content=instruction_message)

        # Pass the instruction message to ChatOpenAI
        llm_chat([system_instruction])

        # Create chain with the initialized ChatOpenAI
        chain = load_qa_chain(llm_chat)

        # Generate LLM response
        try:
            search = docsearch.similarity_search(usr_input)
            response = chain.run(input_documents=search, question=usr_input)
            st.write(response)
        except Exception as e:
            st.write('It looks like you entered an invalid prompt. Please try again.')
            print(e)

    with st.expander('Document Similarity Search'):
        search = docsearch.similarity_search(usr_input)
        st.write(search)
