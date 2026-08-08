# Streamlit UI
import streamlit as st

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

# Sidebar
with st.sidebar:
    st.button(
        "✎ᝰ.  New chat",
        
        use_container_width=True
    )

st.markdown(
    '<div class="chat-welcome">Where should we begin?</div>',
    unsafe_allow_html=True
)

st.chat_input(
    placeholder="Message...",
    accept_file=True,
    file_type=[".pdf", ".txt", ".csv", ".docx", ".py", ".md"]
)

st.markdown(
    '<div class="chat-disclaimer">'
    'Private GPT can make mistakes. Check before using responses'
    '</div>',
    unsafe_allow_html=True
)