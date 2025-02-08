import streamlit as st
import requests
import json
from pathlib import Path
import time
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['USER_AGENT'] = 'myagent'


# Constants
FLASK_BASE_URL = os.getenv("FLASK_BASE_URL")
SUPPORTED_FILE_TYPES = [".pdf"]


def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'documents_loaded' not in st.session_state:
        st.session_state.documents_loaded = False
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'urls' not in st.session_state:
        st.session_state.urls = []
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = set()
    if 'processed_urls' not in st.session_state:
        st.session_state.processed_urls = set()
    if 'current_url' not in st.session_state:
        st.session_state.current_url = ""

def upload_document(file):
    """Upload a document to the Flask backend."""
    if file is not None:
        files = {'file': (file.name, file.getvalue())}  # Read file as bytes
        data = {'source_type': 'file'}
        
        with st.spinner('Uploading and processing document...'):
            response = requests.post(
                f"{FLASK_BASE_URL}/load_source",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                st.session_state.processed_files.add(file.name)
                st.session_state.documents_loaded = True
                return True
            else:
                st.error(f"Error uploading document: {response.json().get('error', 'Unknown error')}")
                return False

def upload_url(url):
    """Upload a URL to the Flask backend."""
    if url:
        data = {
            'source_type': 'url',
            'url': url
        }
        
        with st.spinner('Processing URL...'):
            response = requests.post(
                f"{FLASK_BASE_URL}/load_source",
                data=data
            )
            
            if response.status_code == 200:
                st.session_state.processed_urls.add(url)
                st.session_state.documents_loaded = True
                st.session_state.current_url = ""  # Clear URL after successful processing
                return True
            else:
                st.error(f"Error processing URL: {response.json().get('error', 'Unknown error')}")
                return False

def clear_chat_history():
    """Clear chat history from the Flask backend."""
    with st.spinner('Clearing chat history...'):
        response = requests.post(f"{FLASK_BASE_URL}/clear_chat_history")
        if response.status_code == 200:
            st.session_state.messages = []
            st.success('Chat history cleared successfully!')
        else:
            st.error("Error clearing chat history")

def clear_rag_files():
    """Clear RAG files from the Flask backend."""
    with st.spinner('Clearing RAG files...'):
        response = requests.post(f"{FLASK_BASE_URL}/clear_rag_files")
        if response.status_code == 200:
            st.session_state.processed_files = set()
            st.session_state.processed_urls = set()
            st.session_state.documents_loaded = False
            st.success('RAG files cleared successfully!')
        else:
            st.error("Error clearing RAG files")


def send_message(message):
    """Send a message to the Flask backend and get response."""
    if message:
        with st.spinner('Getting response...'):
            response = requests.post(
                f"{FLASK_BASE_URL}/chat",
                json={"input_message": message}
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                st.error("Error getting response from the server")
                return None

def main():
    st.title("AI Chat Assistant with Document Understanding")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for document upload
    with st.sidebar:
        st.header("Chat related features")
            # Clear chat history button
        if st.button("Clear Chat History", type="secondary"):
            clear_chat_history()

        st.header("Document Upload for RAG search")     
        
        # File upload section
        st.subheader("Upload Files")
        uploaded_files = st.file_uploader(
            "Choose a PDF document",
            type=["pdf"],  # Only allow PDFs
            accept_multiple_files=True,
            help="Only PDF files are supported."
        )

        # Upload button on new line
        upload_button = st.button("Upload Files", type="primary", use_container_width=True)

            
        if upload_button:
            print(f"uploaded_files:{uploaded_files}")
        
        if upload_button and uploaded_files:
            unprocessed_files = [f for f in uploaded_files if f.name not in st.session_state.processed_files]
            if unprocessed_files:
                for file in unprocessed_files:
                    if upload_document(file):
                        st.success(f'Processed: {file.name}')
            else:
                st.info("No new files to process")
        
        # URL input section with spacing
        st.divider()
        st.subheader("Add website URL for RAG search")
        url_input = st.text_input("Enter a website URL", value=st.session_state.current_url)
        st.session_state.current_url = url_input
        # Add URL button on new line
        add_url_button = st.button("Add URL", type="primary", use_container_width=True)
        
        if add_url_button and url_input:
            if url_input not in st.session_state.processed_urls:
                if upload_url(url_input):
                    st.success('URL processed successfully!')
            else:
                st.info("URL already processed")
        
        # Display document status
        st.divider()
        status_container = st.container()
        with status_container:
            if st.session_state.documents_loaded:
                st.success("📚 Documents loaded and ready!")
                
                # Show processed files
                if st.session_state.processed_files:
                    st.write("Processed Files:")
                    for file in st.session_state.processed_files:
                        st.write(f"✅ {file}")
                
                # Show processed URLs
                if st.session_state.processed_urls:
                    st.write("Processed URLs:")
                    for url in st.session_state.processed_urls:
                        st.write(f"✅ {url[:50]}..." if len(url) > 50 else f"✅ {url}")
                
                # Clear all button
                if st.button("Clear All", type="secondary", use_container_width=True):
                    clear_rag_files()  # Clear RAG files
                    st.rerun()
            else:
                st.info("⚠️ No documents loaded yet")
    
    # Main chat interface
    st.subheader("Chat")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        ai_response = send_message(prompt)
        if ai_response:
            # Add AI response to chat history
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            with st.chat_message("assistant"):
                st.markdown(ai_response)

if __name__ == "__main__":
    main()