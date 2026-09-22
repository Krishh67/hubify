import os
from google import genai
from google.genai import types

def get_embedding(text: str) -> list[float]:
    """Generate a 3072-dimensional embedding using Gemini Embedding 2."""
    api_keys = [
        os.environ.get("GEMINI_API_KEY"),
        os.environ.get("GEMINI_API_KEY0"),
        os.environ.get("GEMINI_API_KEY1"),
        os.environ.get("GEMINI_API_KEY2")
    ]
    api_keys = [k for k in api_keys if k]
    if not api_keys:
        raise ValueError("No GEMINI_API_KEY found")

    last_err = None
    for idx, key in enumerate(api_keys):
        client = genai.Client(api_key=key)
        try:
            response = client.models.embed_content(
                model='gemini-embedding-2',
                contents=text,
                config=types.EmbedContentConfig(output_dimensionality=3072)
            )
            return response.embeddings[0].values
        except Exception as e:
            last_err = e
            err_str = str(e).lower()
            if "429" in err_str or "quota" in err_str or "exhausted" in err_str or "rate limit" in err_str:
                continue
            break
    raise RuntimeError(f"Embedding generation failed: {last_err}")
