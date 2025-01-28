import streamlit as st
import tempfile
import os
from config import load_api_keys
from document_processor import DocumentProcessor
from chat_interface import ChatInterface

def initialize_session_state():
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
    
    initialize_session_state()
    
    # Updated CSS with better contrast
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
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #1f1f1f !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2c3e50 !important;
        color: white !important;
    }
    
    /* Primary button style */
    .primary-btn button {
        background-color: #2c3e50 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        text-shadow: none !important;
    }
    .primary-btn button:hover {
        background-color: #34495e !important;
    }
    
    /* Secondary button style */
    .secondary-btn button {
        background-color: #34495e !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        text-shadow: none !important;
    }
    .secondary-btn button:hover {
        background-color: #2c3e50 !important;
    }
    
    /* Document info box */
    .doc-info {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .doc-info h3 {
        color: #2c3e50;
        margin-bottom: 15px;
    }
    
    .doc-info p {
        color: #2c3e50;
        margin-bottom: 8px;
        font-size: 16px;
    }
    
    /* Chat message styling */
    .chat-message {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #e0e0e0;
    }
    
    /* Answer box styling */
    .answer-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2c3e50;
        margin: 15px 0;
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-title"><h1>📚 Interactive Financial statement Analysis System</h1></div>', 
                unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("Configuration")
        
        st.subheader("🔑 API Keys")
        if not st.session_state.api_keys_set:
            gemini_key = st.text_input("Gemini API Key:", type="password")
            llama_key = st.text_input("LlamaParse API Key:", type="password")
            
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("💫 Save API Keys", type="primary", use_container_width=True):
                if gemini_key and llama_key:
                    st.session_state.gemini_api_key = gemini_key
                    st.session_state.llama_api_key = llama_key
                    st.session_state.api_keys_set = True
                    st.success("✅ API keys saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please enter both API keys")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success("✅ API Keys configured")
            st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
            if st.button("🔄 Change API Keys", use_container_width=True):
                st.session_state.api_keys_set = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.api_keys_set:
            st.subheader("📄 Upload Document")
            uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
            
            if 'query_engine' in st.session_state:
                st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
                if st.button("🗑️ Clear Document", use_container_width=True):
                    st.session_state.query_engine = None
                    st.session_state.messages = []
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.api_keys_set and uploaded_file:
        st.markdown(f'''
        <div class="doc-info">
            <h3>📄 Current Document</h3>
            <p><strong>Filename:</strong> {uploaded_file.name}</p>
            <p><strong>Size:</strong> {round(uploaded_file.size/1024, 2)} KB</p>
        </div>
        ''', unsafe_allow_html=True)
        
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
        
        tab1, tab2 = st.tabs(["🔍 Q&A", "💬 Chat"])
        
        with tab1:
            st.subheader("Ask Questions About Your Document")
            question = st.text_input("Your Question:", 
                                   placeholder="Ask anything about the document...",
                                   key="qa_input")
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col2:
                st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
                if st.button("🔍 Get Answer", type="primary", use_container_width=True):
                    if question:
                        with st.spinner('🤔 Thinking...'):
                            response = st.session_state.query_engine.query(question)
                            st.markdown("""
                            <div class="answer-box">
                                <strong>Answer:</strong><br>
                                {response}
                            </div>
                            """.format(response=str(response)), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.subheader("Chat with Your Document")
            chat_interface = ChatInterface(st.session_state.query_engine)
            
            for message in st.session_state.messages:
                st.markdown(f"""
                <div class="chat-message" style="background-color: {'#f0f2f6' if message['role'] == 'assistant' else '#ffffff'}">
                    <strong>{'🤖 Assistant' if message['role'] == 'assistant' else '👤 You'}:</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            
            user_input = st.chat_input("Type your message...")
            if user_input:
                with st.spinner('💭 Processing...'):
                    chat_interface.process_user_input(user_input)
                    st.rerun()
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col2:
                st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
                if st.button("🧹 Clear Chat", use_container_width=True):
                    chat_interface.clear_chat_history()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    
    elif not st.session_state.api_keys_set:
        st.info("👈 Please configure your API keys in the sidebar to begin.")
    else:
        st.info("👈 Please upload a PDF document in the sidebar to begin your analysis.")

if __name__ == "__main__":
    main()
