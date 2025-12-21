"""
Script to build FAISS vector store from marketing knowledge base documents.

Usage:
    python scripts/build_vector_store.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config.settings import settings


def build_vector_store():
    """Build FAISS vector store from knowledge base documents."""
    print("Building vector store from marketing knowledge base...")

    # Check if knowledge base directory exists
    kb_path = Path(settings.rag_knowledge_base_path)
    if not kb_path.exists():
        print(f"Error: Knowledge base directory not found: {kb_path}")
        print(f"Please create the directory and add documents.")
        return

    # Load documents
    print(f"Loading documents from: {kb_path}")
    loader = DirectoryLoader(
        str(kb_path),
        glob="**/*.txt",
        loader_cls=TextLoader,
        show_progress=True,
    )
    documents = loader.load()

    if not documents:
        print("No documents found in knowledge base directory.")
        print("Please add .txt files to the knowledge base directory.")
        return

    print(f"Loaded {len(documents)} documents")

    # Split documents into chunks
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
        length_function=len,
    )
    splits = text_splitter.split_documents(documents)
    print(f"Created {len(splits)} chunks")

    # Initialize embeddings
    print("Initializing embeddings...")
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.openrouter_api_key,
        openai_api_base="https://openrouter.ai/api/v1",
    )

    # Create vector store
    print("Creating FAISS vector store...")
    vectorstore = FAISS.from_documents(splits, embeddings)

    # Save vector store
    vector_store_path = Path(settings.rag_vector_store_path)
    vector_store_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Saving vector store to: {vector_store_path}")
    vectorstore.save_local(str(vector_store_path))

    print("✅ Vector store built successfully!")
    print(f"   - Documents: {len(documents)}")
    print(f"   - Chunks: {len(splits)}")
    print(f"   - Location: {vector_store_path}")


if __name__ == "__main__":
    build_vector_store()
