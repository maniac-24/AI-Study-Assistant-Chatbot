import streamlit as st
import time
import random
import re

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="AI Study Assistant", page_icon="🤖")

# ---------------- CUSTOM CSS ---------------- #
st.markdown("""
<style>

/* User message (right side bubble) */
.user-msg {
    text-align: right;
    background-color: #262730;
    padding: 10px;
    border-radius: 12px;
    margin: 8px 0;
    max-width: 60%;
    margin-left: auto;
}

/* Assistant message (FULL WIDTH) */
.assistant-msg {
    text-align: left;
    background-color: #1c1f26;
    padding: 14px;
    border-radius: 12px;
    margin: 8px auto;
    width: 100%;
    max-width: 900px;
}

/* Remove extra spacing */
.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ---------------- #
st.title("🤖 AI Study Assistant")
st.markdown("🚀 Your smart AI companion for mastering Python, DSA, OS, and DBMS.")

# ---------------- CLEAR CHAT ---------------- #
if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# ---------------- SESSION ---------------- #
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- DISPLAY CHAT ---------------- #
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f"<div class='user-msg'>{message['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='assistant-msg'>{message['content']}</div>",
            unsafe_allow_html=True
        )

# ---------------- USER INPUT ---------------- #
if prompt := st.chat_input("Ask me anything..."):
    if prompt.strip() != "":

        # Show user message
        st.markdown(
            f"<div class='user-msg'>{prompt}</div>",
            unsafe_allow_html=True
        )

        st.session_state.messages.append({"role": "user", "content": prompt})

        prompt_lower = prompt.lower()

        # ---------------- SMART KNOWLEDGE ---------------- #
        knowledge = {
            "python": [
                "Python is a powerful language used in AI, web development, and automation.",
                "Python is beginner-friendly and widely used in data science.",
                "Python supports multiple programming paradigms like OOP and functional programming."
            ],
            "dsa": [
                "DSA stands for Data Structures and Algorithms, essential for coding interviews.",
                "DSA helps in writing efficient and optimized programs.",
                "Learning DSA improves problem-solving skills."
            ],
            "os": [
                "Operating System manages hardware and software resources.",
                "OS acts as an interface between user and computer hardware.",
                "Examples include Windows, Linux, and macOS."
            ],
            "dbms": [
                "DBMS is used to store and manage data efficiently.",
                "It allows users to create, read, update, and delete data.",
                "Examples include MySQL, PostgreSQL, and MongoDB."
            ]
        }

        # Default replies
        default_replies = [
            "I'm your AI Study Assistant. Ask me about Python, DSA, OS, or DBMS.",
            "Try asking about programming topics like Python or DSA.",
            "I can help you learn core CS subjects. What would you like to know?"
        ]

        reply = random.choice(default_replies)

        # Match topic
        matched = False
        clean_prompt = re.sub(r'[^\w\s]', '', prompt_lower)

        for key, responses in knowledge.items():
            if re.search(rf"\b{key}\b", clean_prompt):
                reply = random.choice(responses)
                matched = True
                break

        # Extra smart keywords
        if not matched:
            if any(re.search(rf"\b{word}\b", clean_prompt) for word in ["algorithm", "algorithms", "structure", "structures"]):
                reply = random.choice(knowledge["dsa"])
            elif any(re.search(rf"\b{word}\b", clean_prompt) for word in ["database", "sql", "table", "tables"]):
                reply = random.choice(knowledge["dbms"])
            elif any(re.search(rf"\b{word}\b", clean_prompt) for word in ["linux", "windows", "kernel"]):
                reply = random.choice(knowledge["os"])

        # ---------------- TYPING EFFECT ---------------- #
        with st.spinner("Thinking..."):
            time.sleep(0.3)

        message_placeholder = st.empty()
        full_text = ""

        for word in reply.split():
            full_text += word + " "
            message_placeholder.markdown(
                f"<div class='assistant-msg'>{full_text}▌</div>",
                unsafe_allow_html=True
            )
            time.sleep(0.04)

        message_placeholder.markdown(
            f"<div class='assistant-msg'>{full_text}</div>",
            unsafe_allow_html=True
        )

        st.session_state.messages.append({"role": "assistant", "content": reply})
