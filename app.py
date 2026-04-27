import streamlit as st
from datetime import datetime
from groq import Groq
import os

# ================= CONFIG ================= #
st.set_page_config(page_title="AI Study Assistant", page_icon="🤖")

# ================= API ================= #
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# ================= FUNCTIONS ================= #
def get_time():
    return datetime.now().strftime("%H:%M")

def get_ai_reply(messages):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """You are an expert AI Study Assistant.

STRICT RULES:
- Always use proper Markdown formatting
- Use headings (## Heading)
- Use bullet points (- item)
- Add blank lines between sections
- Keep answers clean and structured
- Do NOT write long paragraphs
- Format like ChatGPT

Example:

## What is Python?
Python is a programming language...

## Key Features
- Easy to learn
- High-level
"""
            },
            *messages
        ]
    )
    return response.choices[0].message.content

# ================= CSS ================= #
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}

/* USER MESSAGE */
.user-msg {
    text-align: right;
    background-color: #262730;
    padding: 12px;
    border-radius: 12px;
    margin: 10px 0;
    max-width: 60%;
    margin-left: auto;
}

/* BOT MESSAGE */
.bot-msg {
    background-color: #1c1f26;
    padding: 16px;
    border-radius: 12px;
    margin: 10px 0;
    width: 100%;
    max-width: 900px;
}

/* TIME */
.time {
    font-size: 11px;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# ================= TITLE ================= #
st.title("AI Study Assistant")
st.markdown("Your smart AI companion for Python, DSA, OS, DBMS")

# ================= CLEAR CHAT ================= #
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# ================= SESSION ================= #
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= DISPLAY CHAT ================= #
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user-msg'>{msg['content']}<br><span class='time'>{msg['time']}</span></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown("<div class='bot-msg'>", unsafe_allow_html=True)
        st.markdown(msg["content"])  # Markdown rendering
        st.markdown(f"<span class='time'>{msg['time']}</span></div>", unsafe_allow_html=True)

# ================= INPUT ================= #
prompt = st.chat_input("Ask me anything...")

if prompt:
    current_time = get_time()

    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "time": current_time
    })

    # Show user message
    st.markdown(
        f"<div class='user-msg'>{prompt}<br><span class='time'>{current_time}</span></div>",
        unsafe_allow_html=True
    )

    # Prepare history
    chat_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # ================= BOT RESPONSE ================= #
    thinking = st.empty()
    thinking.markdown("<div class='bot-msg'>Thinking...</div>", unsafe_allow_html=True)

    reply = get_ai_reply(chat_history)

    thinking.empty()

    assistant_time = get_time()

    # Show response
    st.markdown("<div class='bot-msg'>", unsafe_allow_html=True)
    st.markdown(reply)
    st.markdown(f"<span class='time'>{assistant_time}</span></div>", unsafe_allow_html=True)

    # Store response
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "time": assistant_time
    })