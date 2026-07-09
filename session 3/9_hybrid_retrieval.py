"""
Hybrid retrieval preview — vector search + BM25 keyword search.
Inspired by rag-for-beginners/12_hybrid_search.ipynb (simplified script version).

Run: python 9_hybrid_retrieval.py
"""
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.retrievers import EnsembleRetriever

load_dotenv()

DOCS_PATH = "docs"
PERSIST_DIR = "db/chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

query = "financial aid FAFSA deadline"
print(f"Query: {query}\n")

# Load all chunks as LangChain documents for BM25
loader = DirectoryLoader(path=DOCS_PATH, glob="*.txt", loader_cls=TextLoader)
all_docs = loader.load()

# Vector retriever from Chroma
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
db = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings,
    collection_metadata={"hnsw:space": "cosine"},
)
vector_retriever = db.as_retriever(search_kwargs={"k": 3})

# Keyword retriever
bm25_retriever = BM25Retriever.from_documents(all_docs)
bm25_retriever.k = 3

# Hybrid = weighted blend of both
hybrid_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.7, 0.3],
)

print("=== Vector only ===")
vector_docs = vector_retriever.invoke(query)
for i, doc in enumerate(vector_docs, 1):
    print(f"{i}. {doc.page_content[:120]}...")

print("\n=== Hybrid (70% vector + 30% BM25) ===")
hybrid_docs = hybrid_retriever.invoke(query)
for i, doc in enumerate(hybrid_docs, 1):
    print(f"{i}. {doc.page_content[:120]}...")

print("\nTeaching point: production RAG often combines semantic + keyword search.")
