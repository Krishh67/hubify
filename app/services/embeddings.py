import os
from google import genai
from google.genai import types

def get_embedding(text: str) -> list[float]:
    """Generate a 3072-dimensional embedding using Gemini Embedding 2."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing")
    
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.embed_content(
            model='gemini-embedding-2',
            contents=text,
            config=types.EmbedContentConfig(output_dimensionality=3072)
        )
        return response.embeddings[0].values
    except Exception as e:
        raise RuntimeError(f"Embedding generation failed: {e}")
