import streamlit as st
import tempfile
import os
from config import load_api_keys
from document_processor import DocumentProcessor
from chat_interface import ChatInterface

def initialize_session_state():
    """Initialize session state variables"""
    if 'api_keys_set' not in st.session_state:
        st.session_state.api_keys_set = False
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def main():
    st.set_page_config(
        page_title="Document Q&A and Chat System",
        page_icon="📚",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-title {
        text-align: center;
        padding: 20px;
        color: #1f1f1f;
        background: linear-gradient(90deg, #f0f2f6, #e6e9ef);
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #ffffff;
        border-radius: 5px;
        padding: 10px 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e3d59;
        color: white;
    }
    /* Custom button styles */
    .stButton button {
        background-color: #1e3d59 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
    .stButton button:hover {
        background-color: #2b5480 !important;
    }
    /* Secondary button style */
    .secondary-btn button {
        background-color: #4a4a4a !important;
    }
    .secondary-btn button:hover {
        background-color: #5a5a5a !important;
    }
    /* Document info box */
    .doc-info {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 5px solid #1e3d59;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main title
    st.markdown('<div class="main-title"><h1>📚 Interactive Document Analysis System</h1></div>', 
                unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # API Keys section
        st.subheader("🔑 API Keys")
        if not st.session_state.api_keys_set:
            gemini_key = st.text_input("Gemini API Key:", type="password", 
                                     placeholder="Enter your Gemini API key")
            llama_key = st.text_input("LlamaParse API Key:", type="password", 
                                    placeholder="Enter your LlamaParse API key")
            
            if st.button("💫 Save API Keys", type="primary", use_container_width=True):
                if gemini_key and llama_key:
                    st.session_state.gemini_api_key = gemini_key
                    st.session_state.llama_api_key = llama_key
                    st.session_state.api_keys_set = True
                    st.success("✅ API keys saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please enter both API keys")
        else:
            st.success("✅ API Keys configured")
            with st.container():
                st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
                if st.button("🔄 Change API Keys", type="secondary", use_container_width=True):
                    st.session_state.api_keys_set = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Document upload section (only shown after API keys are set)
        if st.session_state.api_keys_set:
            st.subheader("📄 Upload Document")
            uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
            
            if 'query_engine' in st.session_state:
                st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
                if st.button("🗑️ Clear Document", type="secondary", use_container_width=True):
                    st.session_state.query_engine = None
                    st.session_state.messages = []
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    if st.session_state.api_keys_set and uploaded_file:
        # Display document info
        st.markdown(f'''
        <div class="doc-info">
            <h3>📄 Current Document</h3>
            <p><strong>Filename:</strong> {uploaded_file.name}</p>
            <p><strong>Size:</strong> {round(uploaded_file.size/1024, 2)} KB</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Process document if not already processed
        if 'query_engine' not in st.session_state:
            with st.spinner('🔄 Processing document... Please wait.'):
                processor = DocumentProcessor(
                    gemini_api_key=st.session_state.gemini_api_key,
                    llama_cloud_api_key=st.session_state.llama_api_key
                )
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                st.session_state.query_engine = processor.process_document(tmp_path)
                os.unlink(tmp_path)
        
        # Q&A and Chat tabs
        tab1, tab2 = st.tabs(["🔍 Q&A", "💬 Chat"])
        
        # Q&A Tab
        with tab1:
            st.subheader("Ask Questions About Your Document")
            question = st.text_input("Your Question:", 
                                   placeholder="Ask anything about the document...",
                                   key="qa_input")
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col2:
                if st.button("🔍 Get Answer", type="primary", use_container_width=True):
                    if question:
                        with st.spinner('🤔 Thinking...'):
                            response = st.session_state.query_engine.query(question)
                            st.markdown("### Answer:")
                            st.markdown(f"```{str(response)}```")
        
        # Chat Tab
        with tab2:
            st.subheader("Chat with Your Document")
            chat_interface = ChatInterface(st.session_state.query_engine)
            chat_interface.display_chat_history()
            
            user_input = st.chat_input("Type your message...")
            if user_input:
                with st.spinner('💭 Processing...'):
                    chat_interface.process_user_input(user_input)
                    st.rerun()
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col2:
                st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
                if st.button("🧹 Clear Chat", type="secondary", use_container_width=True):
                    chat_interface.clear_chat_history()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    
    elif not st.session_state.api_keys_set:
        st.info("👈 Please configure your API keys in the sidebar to begin.")
    else:
        st.info("👈 Please upload a PDF document in the sidebar to begin your analysis.")

if __name__ == "__main__":
    main()
