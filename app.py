from google import genai
from google.genai import types
import streamlit as st

st.set_page_config(page_title="Ultra Fast AI", layout="centered")
st.title("⚡ Ultra Fast AI")

# Paste your API key inside the quotes below
client = genai.Client(api_key="AQ.Ab8RN6IYWAYP03Kh5u4NmV_vs0Q17jNhSfk_58o_Nypyk745tw")

user_text = st.text_input("Ask a question:", placeholder="Type here...")

if st.button("Send"):
    if user_text.strip():
        config = types.GenerateContentConfig(
            max_output_tokens=350,
            system_instruction="Provide brief, direct, and immediate answers.",
        )

        def generate():
            response = client.models.generate_content_stream(
                model="gemini-3.5-flash-lite",
                contents=user_text,
                config=config,
            )
            for chunk in response:
                yield chunk.text

        st.write_stream(generate)
    else:
        st.warning("Please type a question first!")
