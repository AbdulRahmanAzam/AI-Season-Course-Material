"""
Shared configuration for the AI Season chatbot.
"""
import os

from dotenv import load_dotenv

load_dotenv()

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Paths
DATA_FILE = os.path.join(_REPO_ROOT, "aiseason-tech", "ai-season.txt")
CHROMA_BASE_DIR = os.path.join(_REPO_ROOT, "db", "chroma_aiseason")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking defaults
DEFAULT_CHUNK_SIZE = 400
DEFAULT_CHUNK_OVERLAP = 40

# Retrieval defaults
DEFAULT_TOP_K = 10
DEFAULT_RETRIEVAL_METHOD = "similarity"

# LLM (Groq — same as root scripts)
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
LLM_TEMPERATURE = 0.2

# All non-LLM chunking strategies supported by this project
CHUNKING_STRATEGIES = [
    "character",
    "recursive",
    "token",
    "sentence_transformers_token",
    "markdown",
    "nltk",
    "line",
    "paragraph",
]
