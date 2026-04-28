import streamlit as st
from datetime import datetime
from groq import Groq
import os
import tempfile

# RAG imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# ================= CONFIG ================= #
st.set_page_config(page_title="AI Study Assistant", page_icon="🤖", layout="wide")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ================= FUNCTIONS ================= #
def get_time():
    return datetime.now().strftime("%H:%M")


@st.cache_resource(show_spinner=False)
def build_vector_db(file_bytes: bytes):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_bytes)
        path = tmp.name

    loader = PyPDFLoader(path)
    docs = loader.load()

    if not docs:
        raise ValueError("No readable content in PDF")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    if not chunks:
        raise ValueError("No chunks created")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    return FAISS.from_documents(chunks, embeddings)


def get_ai_reply(messages, query, context=None):

    if context:
        system_prompt = f"""
You are an AI Study Assistant.

Rules:
- Use Markdown (## headings, bullet points)
- Prefer using the provided context
- If context is relevant → use it
- If context is NOT enough → use your own knowledge to answer

Context:
{context}
"""
    else:
        system_prompt = """
You are an AI Study Assistant.

Rules:
- Use Markdown (## headings, bullet points)
- Give clear, structured answers
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            *messages,
            {"role": "user", "content": query}
        ]
    )

    return response.choices[0].message.content


# ================= SESSION ================= #
if "messages" not in st.session_state:
    st.session_state.messages = []

if "vector_db" not in st.session_state:
    st.session_state.vector_db = None

if "upload_trigger" not in st.session_state:
    st.session_state.upload_trigger = False


# ================= HEADER ================= #
st.markdown("""
<div style="font-size:18px; font-weight:600;">🤖 AI Study Assistant</div>
<div style="font-size:12px; color:gray;">Python • DSA • OS • DBMS</div>
<hr>
""", unsafe_allow_html=True)


# ================= MODE LABEL ================= #
if st.session_state.vector_db:
    st.caption("📄 Answering from PDF")
else:
    st.caption("🌐 General AI mode")


# ================= CHAT DISPLAY ================= #
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div style='text-align:right;background:#262730;padding:10px;border-radius:10px;margin:6px 0;max-width:60%;margin-left:auto'>{msg['content']}<br><span style='font-size:10px;color:gray'>{msg['time']}</span></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div style='background:#1c1f26;padding:12px;border-radius:10px;margin:6px 0;max-width:900px'>{msg['content']}<br><span style='font-size:10px;color:gray'>{msg['time']}</span></div>",
            unsafe_allow_html=True
        )


# ================= INPUT BAR ================= #
st.markdown("---")

col1, col2 = st.columns([1, 11])

with col1:
    if st.button("➕"):
        st.session_state.upload_trigger = True

with col2:
    prompt = st.chat_input("Ask anything...")


# ================= FILE UPLOAD (CHAT STYLE) ================= #
if st.session_state.upload_trigger:
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if uploaded_file:
        try:
            st.session_state.vector_db = build_vector_db(uploaded_file.read())
            st.success("✅ PDF processed successfully")
            st.session_state.upload_trigger = False
        except Exception as e:
            st.error(f"❌ {str(e)}")


# ================= REMOVE PDF ================= #
if st.session_state.vector_db:
    if st.button("Remove PDF"):
        st.session_state.vector_db = None
        st.success("PDF removed")


# ================= MESSAGE FLOW ================= #
if prompt:
    current_time = get_time()

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "time": current_time
    })

    chat_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # ================= RAG LOGIC ================= #
    if st.session_state.vector_db:
        docs = st.session_state.vector_db.similarity_search(prompt, k=3)

        context = "\n\n".join(d.page_content[:500] for d in docs)

        reply = get_ai_reply(chat_history, prompt, context)

    else:
        reply = get_ai_reply(chat_history, prompt, None)

    assistant_time = get_time()

    # Save bot reply
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "time": assistant_time
    })

    st.rerun()


# ================= SIDEBAR ================= #
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()