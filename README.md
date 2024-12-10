# Article Summarization Tool

This is a Streamlit application that allows users to summarize articles, newspapers, research papers, and other text content. The app supports user authentication (Signup/Login) and allows for article processing through URL input. It extracts the text and generates a summary of the content, offering an easy-to-use tool for quick summarization of large articles and documents.

## Features

- **User Authentication**: Users can sign up and log in to access the summarization tool.
- **Summarization of Content**: 
  - Summarize articles, newspapers, research papers, and plain text.
  - Supports automatic extraction of content from URLs.
- **Text Extraction**: The app extracts and processes text from online articles (via URL input) and research papers (via PDF links).
- **Interactive UI**: A clean and responsive user interface built using Streamlit.

## Prerequisites

- Python 3.7+
- Required Python Libraries:
  - `streamlit` (for the app framework)
  - `newspaper3k` (for article processing)
  - `requests` (for making HTTP requests)
  - `nltk` (for Natural Language Processing tasks)
  - `PyMuPDF` (for PDF text extraction)

You can install the required libraries using `pip`:

bash
pip install streamlit newspaper3k requests nltk PyMuPDF

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
