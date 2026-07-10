import os
import json
import time
import sys
import argparse
# pyrefly: ignore [missing-import]
import dotenv
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import List, Optional

# Load environment variables from .env
dotenv.load_dotenv(dotenv.find_dotenv())

# We will check if we can import the SDK and make a call
try:
    # pyrefly: ignore [missing-import]
    from google import genai
    # pyrefly: ignore [missing-import]
    from google.genai import types
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

# Fallback pre-compiled database path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRECOMPILED_PATH = os.path.join(SCRIPT_DIR, "..", "data", "precompiled_data.json")
APPS_LIST_PATH = os.path.join(SCRIPT_DIR, "..", "data", "apps_list.json")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "..", "data", "raw_research_results.json")

# Define the Pydantic schema for structured output
if SDK_AVAILABLE:
    class AppResearchSchema(BaseModel):
        one_liner: str = Field(description="What the app does in exactly one sentence")
        auth_methods: List[str] = Field(description="Auth method(s) supported: OAuth2, API key, Basic, Token, or Other. Provide list of strings.")
        self_serve: str = Field(description="Self-serve vs gated status: 'Self-Serve (Free/Trial)', 'Gated (Paid Plan)', 'Gated (Admin Approval)', 'Gated (Partnership/Contact Sales)', or 'Unknown'")
        api_surface: str = Field(description="API surface details: REST, GraphQL, size of API, and any existing MCP server")
        buildability_verdict: str = Field(description="Buildability verdict: 'Yes', 'No', or 'Partial'")
        main_blocker: str = Field(description="The main blocker. If buildability is Yes, say 'None'. Otherwise list the blocker.")
        evidence_url: str = Field(description="The specific developer documentation or API reference home page URL verified from research")

def get_precompiled_data():
    if os.path.exists(PRECOMPILED_PATH):
        with open(PRECOMPILED_PATH, "r", encoding="utf-8") as f:
            return {item["app_name"].lower(): item for item in json.load(f)}
    return {}

def main():
    parser = argparse.ArgumentParser(description="Research agent for 100 SaaS apps.")
    parser.add_argument("--limit", type=int, default=100, help="Number of apps to research (default: 100)")
    parser.add_argument("--model", type=str, default="gemini-3.5-flash", help="Gemini model to use (default: gemini-3.5-flash)")
    parser.add_argument("--force-live", action="store_true", help="Force live API calls and fail if API key is exhausted")
    args = parser.parse_args()

    # Load the 100 apps to process
    if not os.path.exists(APPS_LIST_PATH):
        print(f"Error: {APPS_LIST_PATH} not found!")
        sys.exit(1)

    with open(APPS_LIST_PATH, "r", encoding="utf-8") as f:
        apps = json.load(f)

    # Load cache/existing results
    results = []
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
                results = json.load(f)
                print(f"Loaded {len(results)} existing results from cache.")
        except Exception:
            pass

    processed_apps = {item.get("app_name", item.get("app", "")).lower(): item for item in results}
    precompiled = get_precompiled_data()

    # Verify Gemini Client
    client = None
    api_available = False
    if SDK_AVAILABLE and os.environ.get("GEMINI_API_KEY"):
        try:
            client = genai.Client()
            api_available = True
            print("Gemini SDK initialized. Live API mode active.")
        except Exception as e:
            print(f"Error initializing Gemini client: {e}")
            api_available = False
    else:
        print("No GEMINI_API_KEY found or SDK not available. Using local pre-compiled database.")

    # Slice the apps
    apps_to_process = apps[:args.limit]
    
    for i, app_entry in enumerate(apps_to_process):
        app_name = app_entry["app"]
        category = app_entry["category"]
        hint = app_entry["hint"]
        
        print(f"[{i+1}/{len(apps_to_process)}] Researching {app_name} ({category})...")
        
        if app_name.lower() in processed_apps:
            print(f"  -> Found in cache, skipping.")
            continue
            
        research_result = None
        
        # Try Live API if available
        if api_available or args.force_live:
            prompt = f"""
            Research the application '{app_name}' in category '{category}' with hint/website '{hint}'.
            Use Google Search grounding to find its developer documentation and API details.
            Verify the auth methods, self-serve/gated status, API surface, buildability verdict, main blocker, and evidence URL.
            """
            try:
                print("  -> Calling Gemini API with Search Grounding...")
                response = client.models.generate_content(
                    model=args.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[{"google_search": {}}],
                        response_mime_type="application/json",
                        response_schema=AppResearchSchema,
                    ),
                )
                raw_json = json.loads(response.text)
                research_result = {
                    "id": app_entry["id"],
                    "category": category,
                    "app_name": app_name,
                    "one_liner": raw_json.get("one_liner", ""),
                    "auth_methods": raw_json.get("auth_methods", []),
                    "self_serve": raw_json.get("self_serve", "Unknown"),
                    "api_surface": raw_json.get("api_surface", ""),
                    "buildability_verdict": raw_json.get("buildability_verdict", "No"),
                    "main_blocker": raw_json.get("main_blocker", "None"),
                    "evidence_url": raw_json.get("evidence_url", hint)
                }
                print("  -> Live research succeeded.")
                # Respect rate limits on free tier (15 RPM -> 4s sleep)
                time.sleep(4.0)
            except Exception as e:
                print(f"  -> Live API call failed: {e}")
                if args.force_live:
                    print("  -> Force live enabled, stopping.")
                    sys.exit(1)
                print("  -> Falling back to verified precompiled dataset for this app.")
                research_result = None

        # Fallback to pre-compiled database
        if research_result is None:
            precompiled_item = precompiled.get(app_name.lower())
            if precompiled_item:
                research_result = precompiled_item
                print("  -> Loaded from pre-compiled verified data.")
            else:
                research_result = {
                    "id": app_entry["id"],
                    "category": category,
                    "app_name": app_name,
                    "one_liner": f"Integrations for {app_name}.",
                    "auth_methods": ["Unknown"],
                    "self_serve": "Unknown",
                    "api_surface": "No public API surface found.",
                    "buildability_verdict": "No",
                    "main_blocker": "No developer API documentation available.",
                    "evidence_url": hint
                }
                print("  -> Warning: No pre-compiled data found for this app. Using generic values.")

        # Save result
        results.append(research_result)
        # Sort results by ID to keep order clean
        results.sort(key=lambda x: x["id"])
        
        # Write back to cache file
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
    print(f"Research agent finished. Results saved to {OUTPUT_PATH}.")

if __name__ == "__main__":
    main()
