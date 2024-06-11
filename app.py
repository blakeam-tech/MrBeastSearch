import os
import shelve
import streamlit as st
from dotenv import load_dotenv
from trufflepig import Trufflepig
from utils.helper_functions import get_youtube_video_title, find_matching_dialogue

# Load environment variables
load_dotenv()

# Streamlit title
st.title("Beast Search")

# Constants for avatars
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# Initialize Trufflepig client
TRUFFLE_PIG_KEY = os.getenv("TRUFFLE_PIG_KEY")
client = Trufflepig(TRUFFLE_PIG_KEY)
index = client.get_index("MrBeastYouTube")

def load_chat_history():
    """Load chat history from a shelve file."""
    with shelve.open("chat_history") as chat_db:
        return chat_db.get("messages", [])

def save_chat_history(messages):
    """Save chat history to a shelve file."""
    with shelve.open("chat_history") as chat_db:
        chat_db["messages"] = messages

def reset_video_search():
    """Reset the state variables related to video search."""
    st.session_state.video_id = None
    st.session_state.transcript = None

# Ensure initialization of session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = load_chat_history()

if 'video_id' not in st.session_state:
    st.session_state.video_id = None

if 'transcript' not in st.session_state:
    st.session_state.transcript = None

# Sidebar with preset search buttons and other controls
preset_searches = {
    "Train Vs Giant Pit": "Drive a train into a pit.",
    "Tank Vs 500000": "Flaming Death Balls",
    "No Food for 30 Days": "Gordon Ramsay"
}

with st.sidebar:
    selected_video = st.selectbox("Select a video", list(preset_searches.keys()))
    input_dialogue = st.text_input("Dialogue", value=preset_searches[selected_video])

    if st.button("Load Preset Searches"):
        st.session_state.video_query = selected_video
        st.session_state.dialogue_search = input_dialogue
        st.session_state.video_id = None  # Trigger the search

    if st.button("Delete Chat History"):
        st.session_state.messages = []
        save_chat_history([])

    if st.button("New Video Search"):
        reset_video_search()

# Display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Main chat interface for video search
if st.session_state.video_id is None:
    if prompt := st.text_input("Enter your video query:", key="video_query", value=st.session_state.get('video_query', '')):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant", avatar=BOT_AVATAR):
            message_placeholder = st.empty()
            response = index.search(query_text=prompt)
            if response and response[0].metadata.get("video_id"):
                video_id = response[0].metadata["video_id"]
                transcript = response[0].metadata.get("transcript", "")
                YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
                video_title = get_youtube_video_title(video_id, YOUTUBE_API_KEY)
                FULL_RESPONSE = f"Found video: {video_title}"
                st.session_state.video_id = video_id
                st.session_state.transcript = transcript
            else:
                FULL_RESPONSE = "No relevant video found."
            message_placeholder.markdown(FULL_RESPONSE)
            st.session_state.messages.append({"role": "assistant", "content": FULL_RESPONSE})

# Dialogue extraction interface
if st.session_state.video_id:
    if dialogue := st.text_input("Enter the specific dialogue you're looking for:", key="dialogue_search", value=st.session_state.get('dialogue_search', '')):
        st.session_state.messages.append({"role": "user", "content": dialogue})
        with st.chat_message("assistant", avatar=BOT_AVATAR):
            transcript = st.session_state.get("transcript", "[]")
            result = find_matching_dialogue(transcript, st.session_state.video_id, dialogue)
            st.write(result)
            st.session_state.messages.append({"role": "assistant", "content": result})

# Save chat history after each interaction
save_chat_history(st.session_state.messages)