import streamlit as st
from openai import OpenAI
import httpx

# 1. Page Configuration
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

    # 5. Core API Execution & Safe Streaming Generator
    with st.chat_message("assistant"):
        try:
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
            
            response = client.chat.completions.create(
                model="openrouter/free",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True
            )
            
            # FIXED: Generator function to unpack chunk lists safely using index [0]
            def response_generator():
                for chunk in response:
                    # Check if choices list exists and contains elements
                    if hasattr(chunk, 'choices') and chunk.choices and len(chunk.choices) > 0:
                        # Extract the first choice element from the list safely
                        first_choice = chunk.choices[0]
                        
                        # Handle both object-style and dict-style chunk structures
                        delta = first_choice.get('delta', None) if isinstance(first_choice, dict) else getattr(first_choice, 'delta', None)
                        
                        if delta:
                            content = delta.get('content', '') if isinstance(delta, dict) else getattr(delta, 'content', '')
                            if content:
                                yield content

            # Stream the generated output cleanly to the window
            full_response = st.write_stream(response_generator())
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
