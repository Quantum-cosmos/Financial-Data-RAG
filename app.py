import streamlit as st
import tempfile
import os
from config import load_api_keys, init_api_keys
from document_processor import DocumentProcessor
from chat_interface import ChatInterface

def main():
    st.set_page_config(
        page_title="Document Q&A and Chat System",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("Document Q&A and Chat System")
    
    # Load API keys
    load_api_keys()
    
    # Initialize API keys
    if not init_api_keys():
        return
    
    # File uploader in sidebar
    with st.sidebar:
        st.header("Document Upload")
        uploaded_file = st.file_uploader("Upload PDF Document", type=['pdf'])
        
        if st.session_state.get('query_engine') and st.button("Clear Document", type="secondary"):
            st.session_state.query_engine = None
            st.session_state.messages = []
            st.rerun()
    
    # Create tabs
    tab1, tab2 = st.tabs(["Document Q&A", "Chat Bot"])
    
    if uploaded_file:
        # Process document if not already processed
        if 'query_engine' not in st.session_state:
            with st.spinner('Processing document... Please wait.'):
                # Get processor instance
                processor = DocumentProcessor(
                    gemini_api_key=st.session_state.gemini_api_key,
                    llama_cloud_api_key=st.session_state.llama_api_key
                )
                
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Process document
                st.session_state.query_engine = processor.process_document(tmp_path)
                
                # Clean up temporary file
                os.unlink(tmp_path)
        
        # Document Q&A tab
        with tab1:
            st.subheader("Ask questions about your document")
            col1, col2 = st.columns([4, 1])
            
            with col1:
                question = st.text_input("Enter your question:")
            with col2:
                submit_button = st.button("Get Answer", type="primary")
            
            if submit_button and question:
                with st.spinner('Getting answer...'):
                    response = st.session_state.query_engine.query(question)
                    st.write("Answer:", str(response))
        
        # Chat Bot tab
        with tab2:
            st.subheader("Chat with your document")
            chat_interface = ChatInterface(st.session_state.query_engine)
            
            # Display chat history
            chat_interface.display_chat_history()
            
            # Chat input
            user_input = st.chat_input("Type your message:")
            if user_input:
                with st.spinner('Processing...'):
                    chat_interface.process_user_input(user_input)
                    st.rerun()
            
            # Clear chat button
            if st.button("Clear Chat History"):
                chat_interface.clear_chat_history()
                st.rerun()
    
    else:
        st.info("👆 Please upload a PDF document to begin.")

if __name__ == "__main__":
    main()
