import os
# pyrefly: ignore [missing-import]
import dotenv
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import List

dotenv.load_dotenv(dotenv.find_dotenv())

client = genai.Client()

class AppResearch(BaseModel):
    category: str = Field(description="Category of the app")
    app_name: str = Field(description="Name of the app")
    one_liner: str = Field(description="What the app does in exactly one sentence")
    auth_methods: List[str] = Field(description="Auth method(s): OAuth2, API key, Basic, Token, or Other")
    self_serve: str = Field(description="Self-serve vs gated status")
    api_surface: str = Field(description="API surface details")
    buildability_verdict: str = Field(description="Buildability verdict: Yes, No, or Partial")
    main_blocker: str = Field(description="Main blocker or None")
    evidence_url: str = Field(description="URL to dev docs")

prompt = """
Research the application Twenty (twenty.com, open-source CRM).
Use Google Search grounding to find its developer documentation and API details.
"""

print("Sending request to Gemini...")
try:
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[{"google_search": {}}],
            response_mime_type="application/json",
            response_schema=AppResearch,
        ),
    )
    print("Response received:")
    print(response.text)
    
    # Grounding metadata (to verify it used search)
    if response.candidates and response.candidates[0].grounding_metadata:
        metadata = response.candidates[0].grounding_metadata
        print("\nGrounding sources used:")
        if metadata.grounding_chunks:
            for chunk in metadata.grounding_chunks:
                if chunk.web:
                    print(f"- {chunk.web.title}: {chunk.web.uri}")
except Exception as e:
    print("Error:", e)
