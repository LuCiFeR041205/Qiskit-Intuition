import os
from google import genai
from google.genai import types

def generate_stream(system_prompt: str, user_prompt: str, api_key: str = None):
    """
    Calls the Gemini API and yields the text chunks for streaming.
    Supports a dynamic api_key argument.
    """
    try:
        # Initialize client with dynamic api_key if provided, otherwise default to env variables
        if api_key:
            client = genai.Client(api_key=api_key)
        else:
            client = genai.Client()
            
        response = client.models.generate_content_stream(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            ),
        )
        for chunk in response:
            yield chunk.text
    except Exception as e:
        yield f"⚠️ **J.A.R.V.I.S. System Error:** Mainframe disconnected. Ensure GEMINI_API_KEY is configured. Details: {e}"
