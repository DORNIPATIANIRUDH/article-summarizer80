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
nltk.download('punkt_tab')


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
        # Check if the username already exists
        user_data = load_user_data()
        if username in user_data:
            st.error('Username already exists. Please choose another one.')
        elif password != confirm_password:
            st.error('Passwords do not match.')
        else:
            # Add the new user to the data
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
            st.session_state['show_login'] = False
            st.session_state['username'] = username
            st.success('Login successful!')
        else:
            st.error('Incorrect username or password')

def main_page():
    st.title('Welcome, ' + st.session_state['username'])
    st.write('You have successfully logged in.')

    st.title('Summarization Tool for Articles, Newspapers, and Research Papers')
    
    # User inputs
    url_or_text = st.text_input("Enter the URL of the article, newspaper, research papers and Text:")
    source_type = st.selectbox("Select the type of content", ["Article", "Newspaper", "Research Paper", "Text"])
    
    if st.button('Process'):
        if url_or_text:
            if source_type == "Article":
                process_article(url_or_text)
            elif source_type == "Newspaper":
                process_newspaper(url_or_text)
            elif source_type == "Research Paper" and url_or_text.lower().endswith(".pdf"):
                process_research_paper(url_or_text)
            elif source_type == "Text":
                process_text(url_or_text)
            else:
                st.warning("Please provide a valid URL and select the appropriate type of content.")
        else:
            st.warning("Please enter a URL or Text.")

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
            st.image(article.top_image, caption="Top Image", use_container_width=True)

        st.write("Article Text:", article.text)
        st.write("Article Summary:", article.summary)
    except Exception as e:
        st.error(f"An error occurred while processing the article: {e}")

def process_newspaper(url):
    try:
        process_article(url)  # Newspapers are processed similarly to articles
    except Exception as e:
        st.error(f"An error occurred while processing the newspaper: {e}")

def process_research_paper(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        
        # Open the PDF
        pdf_file = fitz.open(stream=response.content, filetype="pdf")
        text = ""
        
        # Extract text from each page
        for page_num in range(len(pdf_file)):
            page = pdf_file.load_page(page_num)
            text += page.get_text()
        
        if text.strip() == "":
            st.warning("No text found in the research paper.")
        else:
            st.subheader("Extracted Research Paper Text")
            st.text_area("Full Text:", text, height=300)
            
            # Detect language
            lang = detect(text)
            st.write("Detected Language:", lang)
            
            # Summarize using transformers
            summarizer = pipeline("summarization", model="facebook/mbart-large-cc25")
            summary = summarizer(text[:1024], max_length=150, min_length=50, do_sample=False)  # Limit input to model
            st.subheader("Summarized Research Paper")
            st.write(summary[0]['summary_text'])
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching the PDF: {e}")
    except fitz.FitzError as e:
        st.error(f"An error occurred while processing the PDF: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


def process_text(text):
    try:
        sentences = text.split(".")  # Split into sentences

        # You can implement your own ranking logic here based on length, keywords, etc.
        # For this example, we'll just take the first few sentences
        num_sentences_to_include = 3
        summary = ". ".join(sentences[:num_sentences_to_include]) + "."

        st.subheader("Summarized Text:")
        st.write("Text Summary:", summary)
    
    except Exception as e:  # Catch any unexpected errors
        st.error(f"An error occurred while summarizing the text: {e}")

# Main logic for session control
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_page()
else:
    st.sidebar.title("Login/Signup")
    login_or_signup = st.sidebar.radio("Choose an option", ["Login", "Signup"])
    if login_or_signup == "Login":
        login_page()
    else:
        signup_page()
