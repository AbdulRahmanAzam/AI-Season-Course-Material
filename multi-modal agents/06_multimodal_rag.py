"""
FILE 6: Multimodal RAG
=======================
You already know simple RAG with text:
    chunks -> embeddings -> store -> search -> answer

Multimodal RAG = the SAME idea, but our "documents" are IMAGES.

Our simple recipe (4 steps):
    STEP 1: Describe every image with the VLM  (image -> caption text)
    STEP 2: Turn every caption into an embedding (a list of numbers)
    STEP 3: For a user question -> embed it -> find the closest caption
    STEP 4: Send the WINNING IMAGE + question to the model for the final answer

So we search with text, but we answer with the real image!
"""

import os
import numpy as np
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"
EMBED_MODEL = "gemini-embedding-001"

IMAGE_FOLDER = "images"


# ---------- STEP 1: Caption every image ----------
print("STEP 1: Creating captions for all images...")

image_paths = [
    os.path.join(IMAGE_FOLDER, name)
    for name in os.listdir(IMAGE_FOLDER)
    if name.endswith((".jpg", ".png"))
]

captions = []
for path in image_paths:
    img = Image.open(path)
    response = client.models.generate_content(
        model=MODEL,
        contents=[img, "Describe this image in one short sentence."],
    )
    captions.append(response.text)
    print(f"  {path}  ->  {response.text.strip()}")


# ---------- STEP 2: Embed all captions ----------
print("\nSTEP 2: Converting captions into embeddings...")

result = client.models.embed_content(model=EMBED_MODEL, contents=captions)
caption_embeddings = [e.values for e in result.embeddings]

print(f"  Done! Each caption is now a vector of {len(caption_embeddings[0])} numbers.")


# ---------- STEP 3: Search - find the best image for a question ----------
def cosine_similarity(a, b):
    """How similar are two vectors? 1.0 = identical, 0.0 = unrelated."""
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def find_best_image(question):
    # embed the question
    q = client.models.embed_content(model=EMBED_MODEL, contents=question)
    q_embedding = q.embeddings[0].values

    # compare with every caption
    scores = [cosine_similarity(q_embedding, emb) for emb in caption_embeddings]
    best = int(np.argmax(scores))

    print(f"  Best match: {image_paths[best]}  (score {scores[best]:.2f})")
    return image_paths[best]


# ---------- STEP 4: Answer using the retrieved image ----------
def multimodal_rag(question):
    print(f"\nQUESTION: {question}")
    best_path = find_best_image(question)                # retrieval
    best_image = Image.open(best_path)
    response = client.models.generate_content(           # generation
        model=MODEL,
        contents=[best_image, question],
    )
    print("ANSWER:", response.text.strip())


# ---------- Try it! ----------
multimodal_rag("Which image shows something round and red? Describe it.")
multimodal_rag("Find the shopping bill. What is the total amount?")
