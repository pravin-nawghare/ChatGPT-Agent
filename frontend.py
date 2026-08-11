# Streamlit UI
import streamlit as st
import uuid
import json
import requests


# Initialize current conversation thread id in session state if not already present
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())  # Generate a unique thread ID for the current conversation

if "messages" not in st.session_state:
    st.session_state.messages = []  # Initialize an empty list to store messages for the current conversation

thread_id = st.session_state.thread_id  # Get the current thread ID from session state

st.title("Private GPT",text_alignment="center")

st.set_page_config(
    page_title="Private GPT",
    layout="wide"
)


# Custom button styling
st.markdown("""
<style>
/* Sidebar */ 
section[data-testid="stSidebar"] { 
background-color: #000000; 
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: #ffffff;
}

/* New Chat button */
section[data-testid="stSidebar"] div.stButton > button {
    width: 100%;
    height: 42px:
    text-align: left;
    padding: 0 !important;
    border: none !important;
    border-radius: 8px;
    background: transparent !important;
    color: #ffffff !important;
    box-shadow:none !important;
}

/* Button text container */ 
section[data-testid="stSidebar"] div.stButton > button > div { 
    width: 100%; 
    display: flex; 
    justify-content: flex-start !important; 
    align-items: center; 
    padding-left: 10px; 
}

/* Hover effect */
section[data-testid="stSidebar"] div.stButton > button:hover {
    background-color: #2a2a2a !important;
}

/* Remove focus styling */
section[data-testid="stSidebar"] div.stButton > button:focus { 
    border: none !important; 
    outline: none !important; 
    box-shadow: none !important; 
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>

.chat-welcome {
    text-align: center;
    font-size: 30px;
    font-weight: 400;
    color: white;
    margin-top: 40px;
    margin-bottom: 45px;
}

.chat-disclaimer {
    text-align: center;
    color: #8e8e8e;
    font-size: 12px;
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)

BACKEND_URL = "http://localhost:8080"  # FastAPI backend URL

response = requests.get(f"{BACKEND_URL}/conversations")

if response.status_code == 200:
    conversations = response.json().get("conversations")
else:
    conversations = []

# Sidebar
with st.sidebar:
    if st.button(
        "✎ᝰ.  New chat",
        
        use_container_width=True
    ):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []  # Reset messages for the new conversation
        st.rerun()

    st.markdown("### Recents ")

    for conversation in conversations:
        thread_id_item = conversation["thread_id"]
        title = conversation["title"]

        if st.button(
            title,
            key= f"conversation_{conversation['thread_id']}",
            use_container_width=True
        ):
            st.session_state.thread_id = thread_id_item

            history_response = requests.get(
                f"{BACKEND_URL}/history/{thread_id_item}"
            )

            if history_response.status_code == 200:
                st.session_state.messages = (
                    history_response.json().get("messages")
                )
            st.rerun()

if not st.session_state.messages:
    st.markdown(
        '<div class="chat-welcome">Where should we begin?</div>',
        unsafe_allow_html=True
    )

st.sidebar.divider()

selected_model = st.sidebar.selectbox(
    "Model",
    [
        "gemini-2.5-flash",           
        "gemini-3.0-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash-lite",
        "gemini-3.0-pro",
    ]
)

# Display previous messages
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

user_input = st.chat_input(
    placeholder="Message...",
    accept_file=True,
    file_type=[".pdf", ".txt", ".csv", ".docx", ".py", ".md"]
)

if user_input:
    user_message = user_input.text

    # Handle file upload
    if user_input.files:
        for uploaded_file in user_input.files:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            data = {"thread_id": thread_id}

            uploaded_response = requests.post(
                f"{BACKEND_URL}/upload",
                files=files,
                data=data
            )

            if uploaded_response.status_code == 200:
                result = uploaded_response.json()
                st.success(result["message"])
            else:
                st.error(f"Upload failed: {uploaded_response.text}")

    # store the message
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    # Display the user message
    st.chat_message("user").markdown(user_message)

    # Send to FastAPI
    payload = {
        "message": user_message,
        "thread_id": thread_id,
        "model": selected_model
    }
    st.write("Payload:", payload)
    response = requests.post(
        f"{BACKEND_URL}/chat/stream",
        json=payload,
        headers = {"Content-Type": "application/json"},
        stream=True
    )

    # Display assistant response
    assistant_response = ""

    assistant_container = st.chat_message("assistant")
    placeholder = assistant_container.empty()

    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue

        if line.startswith("data:"):
            data = json.loads(line[5:].strip())

            if "token" in data:
                assistant_response += data["token"]
                placeholder.markdown(assistant_response)

    # Store assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_response
    })
    
st.markdown(
    '<div class="chat-disclaimer">'
    'Private GPT can make mistakes. Check before using responses'
    '</div>',
    unsafe_allow_html=True
)

# Testing
# st.write("Current thread ID:", st.session_state.thread_id)