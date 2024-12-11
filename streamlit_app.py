import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from langdetect import detect
from transformers import pipeline
import fitz  # PyMuPDF
import json
import os
import nltk
nltk.download('punkt')

# Custom CSS for styling
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
            font-family: Arial, sans-serif;
        }
        .reportview-container {
            background-color: transparent;
        }
        .sidebar .sidebar-content {
            background-color: #333;
            color: #fff;
        }
        .main .block-container {
            padding: 2rem;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            transition: background-color 0.3s ease-in-out;
        }
        .main .block-container:hover {
            background-color: #f9f9f9;
        }
        h1, h2, h3 {
            color: #007bff;
            font-weight: bold;
        }
        .stButton button {
            background-color: #007bff;
            color: #fff;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-size: 1rem;
            transition: background-color 0.3s ease;
        }
        .stButton button:hover {
            background-color: #0056b3;
        }
        .stTextInput input, .stTextArea textarea {
            border-radius: 5px;
            border: 1px solid #ccc;
            padding: 0.5rem;
            transition: border-color 0.3s ease;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #007bff;
            outline: none;
        }
        .stSelectbox select {
            border-radius: 5px;
            border: 1px solid #ccc;
            padding: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Path to store user credentials
USER_DATA_FILE = 'user_data.json'

# Load existing user data (if any)
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save user data to file
def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file)

# Streamlit app logic for signup and login
def signup_page():
    st.title('Signup')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    confirm_password = st.text_input('Confirm Password', type='password')

    if st.button('Sign Up'):
        user_data = load_user_data()
        if username in user_data:
            st.error('Username already exists. Please choose another one.')
        elif password != confirm_password:
            st.error('Passwords do not match.')
        else:
            user_data[username] = password
            save_user_data(user_data)
            st.success('Signup successful! You can now log in.')

def login_page():
    st.title('Login')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    if st.button('Login'):
        user_data = load_user_data()
        if username in user_data and user_data[username] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success('Login successful!')
        else:
            st.error('Incorrect username or password')

def main_page():
    st.title(f'Welcome, {st.session_state["username"]}')
    st.title('Summarization Tool for Articles, Newspapers, Research Papers, and Text')

    # User inputs
    url_or_text = st.text_input("Enter the URL or Text:")
    source_type = st.selectbox("Select Content Type", ["Article", "Newspaper", "Research Paper", "Text"])
    
    if st.button('Process'):
        if url_or_text:
            if source_type == "Article":
                process_article(url_or_text)
            elif source_type == "Newspaper":
                process_article(url_or_text)
            elif source_type == "Research Paper" and url_or_text.lower().endswith(".pdf"):
                process_research_paper(url_or_text)
            elif source_type == "Text":
                process_text(url_or_text)
            else:
                st.warning("Invalid input. Please provide a valid URL or text.")
        else:
            st.warning("Please provide a valid URL or text.")

def summarize_multilingual(text):
    try:
        lang = detect(text)
        st.write(f"Detected Language: {lang}")
        summarizer = pipeline("summarization", model="facebook/mbart-large-cc25")
        summary = summarizer(text[:1024], max_length=150, min_length=50, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error in summarization: {e}"

def process_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        if not article.text.strip():
            st.warning("The article appears to be primarily visual (e.g., images or videos) and does not contain extractable text. Summarization is not possible.")
            return

        article.nlp()

        st.subheader("Article Details")
        st.write("Title:", article.title)
        st.write("Authors:", article.authors)
        st.write("Publish Date:", article.publish_date)
        if article.top_image:
            st.image(article.top_image, caption="Top Image")

        st.write("Article Text:", article.text)
        summary = summarize_multilingual(article.text)
        st.subheader("Article Summary")
        st.write(summary)
    except Exception as e:
        st.error(f"Error while processing the article: {e}")

def process_research_paper(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        pdf_file = fitz.open(stream=response.content, filetype="pdf")
        text = ""
        for page in pdf_file:
            text += page.get_text()
        if not text.strip():
            st.warning("The research paper appears to be primarily visual (e.g., images or diagrams) and does not contain extractable text. Summarization is not possible.")
            return
        summary = summarize_multilingual(text)
        st.subheader("Summarized Research Paper")
        st.write(summary)
    except Exception as e:
        st.error(f"Error while processing the research paper: {e}")

def process_text(text):
    try:
        summary = summarize_multilingual(text)
        st.subheader("Text Summary")
        st.write(summary)
    except Exception as e:
        st.error(f"Error while processing the text: {e}")

# Main logic for session control
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_page()
else:
    st.sidebar.title("Login/Signup")
    option = st.sidebar.radio("Choose an option", ["Login", "Signup"])
    if option == "Login":
        login_page()
    else:
        signup_page()
