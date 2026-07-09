"""
Retrieval methods — similarity, score threshold, MMR.
Same style as rag-for-beginners/9_retrieval_methods.py

Run: python 6_retrieval_methods.py
"""
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

PERSIST_DIR = "db/chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

db = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"},
)

query = "What is the in-state tuition?"
print(f"Query: {query}\n")

# METHOD 1: Basic similarity
print("=== METHOD 1: Similarity Search (k=3) ===")
retriever = db.as_retriever(search_kwargs={"k": 3})
docs = retriever.invoke(query)
for i, doc in enumerate(docs, 1):
    print(f"Document {i}: {doc.page_content[:200]}...\n")

print("-" * 60)

# METHOD 2: Score threshold (uncomment to try)
# print("\n=== METHOD 2: Similarity with Score Threshold ===")
# retriever = db.as_retriever(
#     search_type="similarity_score_threshold",
#     search_kwargs={"k": 3, "score_threshold": 0.3},
# )
# docs = retriever.invoke(query)
# for i, doc in enumerate(docs, 1):
#     print(f"Document {i}: {doc.page_content[:200]}...\n")

# METHOD 3: MMR (uncomment to try)
# print("\n=== METHOD 3: Maximum Marginal Relevance ===")
# retriever = db.as_retriever(
#     search_type="mmr",
#     search_kwargs={"k": 3, "fetch_k": 10, "lambda_mult": 0.5},
# )
# docs = retriever.invoke(query)
# for i, doc in enumerate(docs, 1):
#     print(f"Document {i}: {doc.page_content[:200]}...\n")

print("Done. Try different k values and search types.")
