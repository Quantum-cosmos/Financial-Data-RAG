import logging
from typing import List
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_parse import LlamaParse
import chromadb
import google.generativeai as genai

class DocumentProcessor:
    def __init__(self, gemini_api_key: str, llama_cloud_api_key: str):
        """Initialize document processor with API keys"""
        self.gemini_api_key = gemini_api_key
        self.llama_cloud_api_key = llama_cloud_api_key
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        
        # Initialize Gemini LLM
        self.llm = Gemini(
            model="models/gemini-1.5-flash",
            api_key=self.gemini_api_key,
            temperature=0.3,
            top_p=0.85,
            max_tokens=4096
        )
        
        # Initialize embeddings
        self.embed_model = GeminiEmbedding(
            model="models/embedding-001",
            api_key=self.gemini_api_key,
            dimension=768
        )
        
        # Set global configurations
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        
        # Initialize Chroma client
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    def process_document(self, file_path: str, collection_name: str):
        """Process document and create query engine"""
        # Parse document
        documents = self.parse_document(file_path)
        
        # Process nodes
        nodes = self.process_nodes(documents)
        
        # Create RAG pipeline
        query_engine = self.create_rag_pipeline(nodes, collection_name)
        
        return query_engine
    
    def parse_document(self, file_path: str) -> List:
        """Parse document using LlamaParse"""
        parser = LlamaParse(
            api_key=self.llama_cloud_api_key,
            result_type="markdown"
        )
        return parser.load_data(file_path)
    
    def process_nodes(self, documents: List) -> List:
        """Process documents into nodes"""
        node_parser = SimpleNodeParser.from_defaults(
            chunk_size=1024,
            chunk_overlap=200
        )
        return node_parser.get_nodes_from_documents(documents)
    
    def create_rag_pipeline(self, nodes: List, collection_name: str):
        """Create RAG pipeline with vector store"""
        # Create or get collection
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
        except:
            collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        
        # Create vector store and index
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        index = VectorStoreIndex(
            nodes=nodes,
            storage_context=storage_context,
            show_progress=True
        )
        
        return index.as_query_engine(
            similarity_top_k=3,
            response_mode="compact"
        )