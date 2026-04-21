import streamlit as st
import time

# Configure page settings
st.set_page_config(page_title="AI Study Assistant", page_icon="🤖")

st.title("🤖 AI Study Assistant")
st.markdown("Your minimal, modern study companion for Python, DSA, OS, and DBMS.")

# Add Clear Chat Button at top (sidebar)
if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input using st.chat_input
if prompt := st.chat_input("Ask me anything..."):
    if prompt.strip() != "":
        # Display user message in chat bubble
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Simple logic based on dictionary (cleaner + scalable)
        prompt_lower = prompt.lower()
        
        knowledge = {
            "python": "Python is a versatile programming language used for AI, web development, data science, and more.",
            "dsa": "DSA stands for Data Structures and Algorithms. Essential for problem solving.",
            "os": "Operating System manages hardware and software resources.",
            "dbms": "DBMS is used to store and manage databases efficiently."
        }

        reply = "I'm your AI Study Assistant 🤖. Ask me about Python, DSA, OS, or DBMS!"

        for key, value in knowledge.items():
            if key in prompt_lower:
                reply = value
                break

        # Display assistant response in chat bubble with typing effect
        with st.spinner("Assistant is thinking... 🤔"):
            time.sleep(0.5)
            
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_text = ""
            
            for word in reply.split():
                full_text += word + " "
                message_placeholder.markdown(full_text + "▌")
                time.sleep(0.05)  # Added slight delay for a realistic typing effect
            
            message_placeholder.markdown(full_text)
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": reply})