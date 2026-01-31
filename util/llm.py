
import os
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import numpy as np

# Global embedding model (lazy load)
_embed_model = None

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        print("Loading embedding model (all-MiniLM-L6-v2)...")
        # Use a small, fast model
        _embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embed_model

def get_embedding(text):
    """Generates a vector embedding for the given text."""
    model = get_embed_model()
    # Normalize text
    text = text.replace("\n", " ")
    embedding = model.encode(text)
    return embedding

def generate_answer(query, context_chunks):
    """
    Generates an answer using Google Gemini Pro.
    context_chunks: List of strings (text chunks)
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "Error: GOOGLE_API_KEY not set in environment."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

    # Construct Prompt
    context_text = "\n\n---\n\n".join(context_chunks)
    prompt = f"""You are a helpful assistant analyzing Florida State contracts.
Use the following context to answer the user's question. 
If the answer is not in the context, say so.
Keep the answer concise and professional.

Context:
{context_text}

Question: {query}
Answer:"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error gathering response from Gemini: {str(e)}"
