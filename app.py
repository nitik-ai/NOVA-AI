import io
import json
import os
import urllib.parse
from google import genai
from google.genai import types
from PIL import Image
import streamlit as st

st.set_page_config(page_title="NOVA AI", layout="wide")

# --- Permanent Storage Configuration ---
DATA_FILE = "chat_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"chats": {"New Session": []}, "current_chat": "New Session"}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

db = load_data()

# --- Custom Styling: Pure White Canvas, Black Fonts, No Streamlit Branding ---
st.markdown("""
<style>
    /* HIDE STREAMLIT BRANDING, HEADER, AND DEPLOY BUTTON */
    #MainMenu {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    div[data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    div[data-testid="stDecoration"] {visibility: hidden !important; display: none !important;}
    div[data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
    .stAppDeployButton {display: none !important;}

    /* Full White Background */
    .stApp {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* All typography forced to black */
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp div {
        color: #000000 !important;
    }

    /* Left Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] * {
        color: #000000 !important;
    }

    /* Main Chat Container */
    .main .block-container {
        max-width: 860px;
        padding-top: 1.5rem;
        padding-bottom: 9rem !important;
    }

    /* NOVA AI Multi-Color Gradient Greeting */
    .nova-hero {
        padding: 10px 0 15px 0;
        text-align: left;
    }
    .nova-gradient-text {
        font-size: 3.4rem;
        font-weight: 700;
        background: linear-gradient(74deg, #4285F4 0%, #9B72CB 15%, #D96570 30%, #F4B400 45%, #4285F4 60%);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        line-height: 1.2;
        margin-bottom: 6px;
    }
    .nova-subtext {
        font-size: 1.9rem;
        font-weight: 500;
        color: #475569 !important;
        letter-spacing: -0.5px;
    }

    /* User Question Bubble */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background-color: #f1f5f9 !important;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 12px 18px;
        margin-bottom: 16px;
        max-width: 85%;
        margin-left: auto;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) p {
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 1.05rem;
    }

    /* Assistant Bubble */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background-color: transparent !important;
        border: none !important;
        padding: 8px 12px;
        margin-bottom: 20px;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) p {
        color: #1e293b !important;
        font-size: 1.05rem;
        line-height: 1.6;
    }

    /* Input Pill Bar */
    div[data-testid="stChatInput"] {
        background-color: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 30px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }
    div[data-testid="stChatInput"] textarea {
        color: #000000 !important;
        background-color: transparent !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
    }

    /* Upload Button in Black */
    div[data-testid="stFileUploader"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 14px !important;
        padding: 3px !important;
    }
    div[data-testid="stFileUploader"] button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: none !important;
    }
    div[data-testid="stFileUploader"] button * {
        color: #ffffff !important;
    }
    div[data-testid="stFileUploader"] button:hover {
        background-color: #27272a !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 14px;
        background-color: #ffffff;
        color: #000000 !important;
        border: 1px solid #cbd5e1;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #f1f5f9;
        border-color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# --- Put Your Gemini API Key Here ---
API_KEY = "AQ.Ab8RN6L3eMY_NBHBTv004ZAdKM-u11VTyQgaLWtXgl7DSv4w9g"
client = genai.Client(api_key=API_KEY)

# --- Ensure Active Session Exists ---
current_chat = db.get("current_chat", "New Session")
if current_chat not in db["chats"]:
    db["chats"][current_chat] = []

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("### NOVA AI")

    # Multitasking Mode Selector
    st.markdown("##### ⚙️ Task Mode")
    task_mode = st.selectbox(
        "Choose Mode:",
        [
            "💬 General Assistant",
            "🎨 Image Generator",
            "🔬 Academic & STEM Tutor",
            "📝 Document Summarizer"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # + New Chat Button
    if st.button("➕  New chat", use_container_width=True):
        new_chat_name = "New Session"
        db["chats"][new_chat_name] = []
        db["current_chat"] = new_chat_name
        save_data(db)
        st.rerun()

    st.markdown("---")

    # Topic-Named History List
    st.markdown("##### Recent Topics")
    for chat_name in list(db["chats"].keys()):
        col_select, col_del = st.columns([4, 1])
        with col_select:
            is_active = "✨ " if chat_name == db["current_chat"] else "💬 "
            display_title = chat_name if len(chat_name) <= 22 else chat_name[:22] + "..."
            if st.button(f"{is_active}{display_title}", key=f"sel_{chat_name}", use_container_width=True):
                db["current_chat"] = chat_name
                save_data(db)
                st.rerun()
        with col_del:
            if len(db["chats"]) > 1:
                if st.button("✕", key=f"del_{chat_name}"):
                    del db["chats"][chat_name]
                    db["current_chat"] = list(db["chats"].keys())[0]
                    save_data(db)
                    st.rerun()

# --- Center Screen Hero Greeting with Logo ---
active_messages = db["chats"][db["current_chat"]]

if not active_messages:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=95)
    st.markdown("""
        <div class="nova-hero">
            <div class="nova-gradient-text">Hello</div>
            <div class="nova-subtext">How can NOVA AI assist you today?</div>
        </div>
    """, unsafe_allow_html=True)

# --- Top Area: Display Messages ---
chat_container = st.container()
with chat_container:
    for msg in active_messages:
        avatar_icon = "👤" if msg["role"] == "user" else "⚡"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            if msg.get("type") == "image":
                st.image(msg["content"], caption="Generated by NOVA AI", use_container_width=True)
            else:
                st.markdown(msg["content"])

# --- Bottom Bar: Fixed Downside Input Controls ---
prompt = None
uploaded_file = None

if hasattr(st, "bottom"):
    with st.bottom:
        in_col, up_col = st.columns([5, 1])
        with up_col:
            uploaded_file = st.file_uploader(
                "Upload",
                type=["pdf", "png", "jpg", "jpeg", "txt"],
                label_visibility="collapsed",
                key=f"uploader_{db['current_chat']}"
            )
        with in_col:
            prompt = st.chat_input("Ask NOVA AI or type 'generate image of...'")
else:
    in_col, up_col = st.columns([5, 1])
    with up_col:
        uploaded_file = st.file_uploader(
            "Upload",
            type=["pdf", "png", "jpg", "jpeg", "txt"],
            label_visibility="collapsed",
            key=f"uploader_{db['current_chat']}"
        )
    with in_col:
        prompt = st.chat_input("Ask NOVA AI or type 'generate image of...'")

# --- Helper: Check if User Prompt Requests an Image ---
def is_image_request(text, mode):
    if "Image Generator" in mode:
        return True
    triggers = ["generate image", "create image", "draw", "make an image", "picture of", "photo of", "paint"]
    return any(t in text.lower() for t in triggers)

# --- Processing Search Prompt ---
if prompt:
    # 1. Rename 'New Session' to the actual topic question
    if db["current_chat"] == "New Session" or len(db["chats"][db["current_chat"]]) == 0:
        new_title = prompt.strip()[:32]
        if new_title in db["chats"]:
            new_title = f"{new_title} ({len(db['chats'])})"
        db["chats"][new_title] = db["chats"].pop(db["current_chat"], [])
        db["current_chat"] = new_title

    # 2. Save user prompt permanently
    db["chats"][db["current_chat"]].append({"role": "user", "content": prompt, "type": "text"})
    save_data(db)

    # 3. Render user prompt in the top chat area
    with chat_container:
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

    # 4. Multitasking Branch: Image Generation vs Text Reasoning
    if is_image_request(prompt, task_mode):
        with chat_container:
            with st.chat_message("assistant", avatar="⚡"):
                with st.spinner("🎨 Generating your watermark-free image..."):
                    try:
                        clean_prompt = urllib.parse.quote(prompt.strip())
                        img_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?model=flux-schnell&width=768&height=768&nologo=true"

                        st.image(img_url, caption=f"Created for: {prompt}", use_container_width=True)
                        db["chats"][db["current_chat"]].append({"role": "assistant", "content": img_url, "type": "image"})
                        save_data(db)
                    except Exception as err:
                        st.error(f"Image generation error: {err}")
    else:
        system_rules = {
            "💬 General Assistant": "You are NOVA AI, a smart, fast, and helpful assistant. Format answers cleanly using markdown, bold headers, and bullet points.",
            "🔬 Academic & STEM Tutor": "You are NOVA STEM Tutor. Break down complex science and math problems step-by-step with clear formulas, biological diagrams, and structured notes.",
            "📝 Document Summarizer": "You are NOVA Document Specialist. Focus strictly on summarizing key takeaways, extracting core points, and outlining study revisions from the provided text or attachments."
        }
        active_instruction = system_rules.get(task_mode, system_rules["💬 General Assistant"])

        contents_payload = []
        if uploaded_file is not None:
            contents_payload.append(
                types.Part.from_bytes(
                    data=uploaded_file.getvalue(),
                    mime_type=uploaded_file.type
                )
            )
        contents_payload.append(prompt)

        # 5. Stream Assistant Response inside the upper chat container
        with chat_container:
            with st.chat_message("assistant", avatar="⚡"):
                config = types.GenerateContentConfig(
                    max_output_tokens=1400,
                    system_instruction=active_instruction,
                )

                def response_stream():
                    response = client.models.generate_content_stream(
                        model="gemini-3.5-flash",
                        contents=contents_payload,
                        config=config,
                    )
                    for chunk in response:
                        yield chunk.text

                full_response = st.write_stream(response_stream)
                db["chats"][db["current_chat"]].append({"role": "assistant", "content": full_response, "type": "text"})
                save_data(db)