import streamlit as st
from openai import OpenAI
import httpx

# 1. Page Config
st.set_page_config(page_title="Universal Free Chatbot", page_icon="🤖")
st.title("🤖 Universal Free AI Assistant")

# 2. Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter OpenRouter API Key", type="password", help="Get a free key from openrouter.ai")
    st.markdown("[Get a Free OpenRouter API Key](https://openrouter.ai/)")
    st.info("System Route: openrouter/free (Auto-selects active free models)")

# 3. Chat History Setup
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. User Prompt Handling
if prompt := st.chat_input("What is on your mind?"):
    if not api_key:
        st.info("Please add your OpenRouter API key in the sidebar to continue.")
        st.stop()
        
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 5. Core API Execution Window
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Set up a generic network client to bypass rigid proxy barriers
            http_client = httpx.Client(timeout=httpx.Timeout(45.0, connect=10.0))
            
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                http_client=http_client,
                default_headers={
                    "HTTP-Referer": "http://localhost:8501", 
                    "X-Title": "Streamlit Free App"      
                }
            )
            
            # Use the universal router instead of individual model IDs
            response = client.chat.completions.create(
                model="openrouter/free",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True
            )
            
            for chunk in response:
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    delta = chunk.choices.delta
                    if hasattr(delta, 'content') and delta.content:
                        full_response += delta.content
                        message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
