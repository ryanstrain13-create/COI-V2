import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        pass
        
if api_key:
    genai.configure(api_key=api_key)

def generate_with_retry(prompt):
    """Attempts generation with multiple models in case of availability issues."""
    # Priority: Flash (Fastest) -> 1.5 Pro (Best) -> 1.0 Pro (Legacy Fallback)
    models_to_try = ["fake-model-to-fail", "gemini-1.5-flash", "gemini-pro"]
    errors = []

    print(f"DEBUG: Trying models: {models_to_try}")

    for model_name in models_to_try:
        try:
            print(f"Attempting {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            print(f"✅ Success with {model_name}")
            return response
        except Exception as e:
            print(f"❌ Failed {model_name}: {e}")
            errors.append(f"{model_name}: {str(e)}")
            continue

    error_msg = "\n".join(errors)
    raise Exception(f"All available models failed.\nDetails:\n{error_msg}")

if __name__ == "__main__":
    if not api_key:
        print("Skipping test: No API Key")
    else:
        try:
            res = generate_with_retry("Say 'Test Passed'")
            print(f"Final Result: {res.text}")
        except Exception as e:
            print(f"Final Error: {e}")
