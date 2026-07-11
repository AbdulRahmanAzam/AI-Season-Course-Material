"""
Chunking demo — CharacterTextSplitter vs RecursiveCharacterTextSplitter.
Same style as rag-for-beginners/5_recursive_character_text_spliiter.py

Run: python 5_recursive_chunking_demo.py
"""
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

sample_text = """Riverside University — Tuition FAQ

Q: What is in-state tuition?
A: In-state undergraduate tuition is $12,400 per year.

Q: How do I apply for financial aid?
A: Submit the FAFSA by February 1.

This is one very long paragraph with no double newlines inside it so a basic character splitter may cut awkwardly in the middle of a sentence which is why recursive splitting is often better for real documents."""


print("=== 1. CharacterTextSplitter (chunk_size=120) ===")
splitter1 = CharacterTextSplitter(chunk_size=120, chunk_overlap=20)
chunks1 = splitter1.split_text(sample_text)
for i, chunk in enumerate(chunks1, 1):
    print(f"Chunk {i} ({len(chunk)} chars): {chunk}\n")

print("=" * 60)
print("=== 2. RecursiveCharacterTextSplitter (chunk_size=120) ===")
recursive_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " ", ""],
    chunk_size=120,
    chunk_overlap=20,
)
chunks2 = recursive_splitter.split_text(sample_text)
for i, chunk in enumerate(chunks2, 1):
    print(f"Chunk {i} ({len(chunk)} chars): {chunk}\n")

print("Teaching point: chunking strategy affects retrieval quality.")
