import streamlit as st
import tempfile
import os
from config import load_api_keys, init_api_keys
from document_processor import DocumentProcessor
from chat_interface import ChatInterface

def main():
    st.title("Document Q&A and Chat System")
    
    # Load API keys
    load_api_keys()
    
    # Initialize API keys
    if not init_api_keys():
        return
    
    # Create tabs
    tab1, tab2 = st.tabs(["Document Q&A", "Chat Bot"])
    
    # Get processor instance
    processor = DocumentProcessor(
        gemini_api_key=st.session_state.gemini_api_key,
        llama_cloud_api_key=st.session_state.llama_api_key
    )
    
    # File uploader in sidebar
    uploaded_file = st.sidebar.file_uploader("Upload Document", type=['pdf'])
    
    if uploaded_file:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Process document
        query_engine = processor.process_document(
            tmp_path,
            collection_name=f"collection_{uploaded_file.name}"
        )
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        # Document Q&A tab
        with tab1:
            st.subheader("Ask questions about your document")
            question = st.text_input("Enter your question:")
            
            if st.button("Get Answer"):
                if question:
                    response = query_engine.query(question)
                    st.write("Answer:", str(response))
        
        # Chat Bot tab
        with tab2:
            st.subheader("Chat with your document")
            chat_interface = ChatInterface(query_engine)
            
            # Display chat history
            chat_interface.display_chat_history()
            
            # Chat input
            user_input = st.chat_input("Type your message:")
            if user_input:
                chat_interface.process_user_input(user_input)
            
            # Clear chat button
            if st.button("Clear Chat"):
                chat_interface.clear_chat_history()
    
    else:
        st.info("Please upload a document to begin.")

if __name__ == "__main__":
    main()