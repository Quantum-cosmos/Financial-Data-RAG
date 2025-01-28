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

def api_key_section():
    """API Key input section with improved styling"""
    st.markdown("""
    <style>
    .api-section {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='api-section'>", unsafe_allow_html=True)
        st.subheader("🔑 API Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            gemini_key = st.text_input("Gemini API Key:", type="password", 
                                     placeholder="Enter your Gemini API key")
        with col2:
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
        
        st.markdown("</div>", unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Document Q&A and Chat System",
        page_icon="📚",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Custom CSS for styling
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
        background-color: #0e4c92;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main title with styling
    st.markdown('<div class="main-title"><h1>📚 Interactive Document Analysis System</h1></div>', 
                unsafe_allow_html=True)
    
    # Check if API keys are set
    if not st.session_state.api_keys_set:
        api_key_section()
        return
    
    # Document upload section
    st.markdown("### 📄 Upload Your Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'], 
                                   help="Upload a PDF document to analyze")
    
    if uploaded_file:
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
        
        # Create tabs with custom styling
        tab1, tab2 = st.tabs(["🔍 Document Q&A", "💬 Interactive Chat"])
        
        # Q&A Tab
        with tab1:
            st.markdown("""
            <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px;'>
                <h3 style='margin-bottom: 20px;'>Ask Questions About Your Document</h3>
            </div>
            """, unsafe_allow_html=True)
            
            with st.container():
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
            st.markdown("""
            <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px;'>
                <h3 style='margin-bottom: 20px;'>Chat with Your Document</h3>
            </div>
            """, unsafe_allow_html=True)
            
            chat_interface = ChatInterface(st.session_state.query_engine)
            chat_interface.display_chat_history()
            
            # Chat input with improved styling
            user_input = st.chat_input("Type your message...")
            if user_input:
                with st.spinner('💭 Processing...'):
                    chat_interface.process_user_input(user_input)
                    st.rerun()
            
            # Clear chat button with improved styling
            col1, col2, col3 = st.columns([3, 1, 1])
            with col2:
                if st.button("🧹 Clear Chat", type="secondary", use_container_width=True):
                    chat_interface.clear_chat_history()
                    st.rerun()
        
        # Clear document button in sidebar
        with st.sidebar:
            if st.button("🗑️ Clear Document", type="secondary", use_container_width=True):
                st.session_state.query_engine = None
                st.session_state.messages = []
                st.rerun()
    
    else:
        st.info("👆 Please upload a PDF document to begin your analysis.")

if __name__ == "__main__":
    main()
