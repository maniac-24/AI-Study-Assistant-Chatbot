import streamlit as st
from groq import Groq
import os
import tempfile
import time

# RAG
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# ================= CONFIG ================= #
st.set_page_config(page_title="AI Study Assistant", page_icon="🤖", layout="wide")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ================= SESSION ================= #
if "messages" not in st.session_state:
    st.session_state.messages = []

if "vector_db" not in st.session_state:
    st.session_state.vector_db = None

if "show_upload" not in st.session_state:
    st.session_state.show_upload = False

# ================= BUILD VECTOR DB ================= #
@st.cache_resource(show_spinner=False)
def build_vector_db(file_bytes):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_bytes)
        path = tmp.name

    loader = PyPDFLoader(path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_documents(chunks, embeddings)

# ================= AI ================= #
def get_ai_reply(messages, query, context=None):

    if context:
        system_prompt = f"""
You are an AI Study Assistant.

Rules:
- Use document as primary source
- If not found → say "NOT_FOUND"
- Do not hallucinate

Context:
{context}
"""
    else:
        system_prompt = """
You are an AI Study Assistant.

Rules:
- Answer clearly
- Use structured format
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

# ================= STREAM ================= #
def stream_text(text):
    placeholder = st.empty()
    output = ""

    for char in text:
        output += char
        placeholder.markdown(output)
        time.sleep(0.002)

    return output

# ================= HEADER ================= #
st.markdown("""
<div style="font-size:18px;font-weight:600;">🤖 AI Study Assistant</div>
<div style="font-size:12px;color:gray;">Python • DSA • OS • DBMS</div>
<hr>
""", unsafe_allow_html=True)

# ================= MODE ================= #
if st.session_state.vector_db:
    st.caption("📄 PDF Mode (Smart RAG)")
else:
    st.caption("🌐 General AI Mode")

# ================= CHAT ================= #
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div style='text-align:right;background:#262730;padding:10px;border-radius:10px;margin:6px 0;max-width:60%;margin-left:auto'>{msg['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div style='background:#1c1f26;padding:12px;border-radius:10px;margin:6px 0'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

# ================= INPUT ================= #
st.markdown("---")
col1, col2 = st.columns([1, 10])

with col1:
    if st.button("➕"):
        st.session_state.show_upload = not st.session_state.show_upload

with col2:
    prompt = st.chat_input("Ask about your PDF...")

# ================= UPLOAD ================= #
if st.session_state.show_upload:
    files = st.file_uploader("Upload PDF", type="pdf", accept_multiple_files=True)

    if files:
        st.session_state.vector_db = None

        for f in files:
            db = build_vector_db(f.read())

            if st.session_state.vector_db is None:
                st.session_state.vector_db = db
            else:
                st.session_state.vector_db.merge_from(db)

        st.success("PDF Loaded ✅")
        st.session_state.show_upload = False

# ================= REMOVE ================= #
if st.session_state.vector_db:
    if st.button("Remove PDFs"):
        st.session_state.vector_db = None
        st.success("Removed")

# ================= MAIN ================= #
if prompt:

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    chat_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    reply = ""

    if st.session_state.vector_db:

        # 🔍 Retrieve
        docs = st.session_state.vector_db.similarity_search(prompt, k=5)
        context = "\n\n".join(d.page_content for d in docs)

        if context.strip():

            # STEP 1 → Try document
            doc_reply = get_ai_reply(chat_history, prompt, context)

            # STEP 2 → fallback detection
            if "NOT_FOUND" in doc_reply:
                reply = get_ai_reply(chat_history, prompt, context=None)
            else:
                reply = doc_reply

        else:
            reply = get_ai_reply(chat_history, prompt, context=None)

    else:
        reply = get_ai_reply(chat_history, prompt, context=None)

    # ================= OUTPUT ================= #
    st.markdown("<div style='background:#1c1f26;padding:12px;border-radius:10px'>", unsafe_allow_html=True)
    final = stream_text(reply)
    st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": final})

    st.rerun()

# ================= CLEAR ================= #
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()