"""Module for searching and managing chat history related to MrBeast's YouTube videos using Streamlit."""

import os
import shelve
import streamlit as st
from dotenv import load_dotenv
from trufflepig import Trufflepig
from utils import get_youtube_video_title, find_matching_dialogue

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
    if "video_id" in st.session_state:
        del st.session_state["video_id"]
    if "transcript" in st.session_state:
        del st.session_state["transcript"]

# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Sidebar with a button to delete chat history
with st.sidebar:
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

# Main chat interface
if "video_id" not in st.session_state:
    if prompt := st.chat_input("Enter your video query:", key="video_query"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=BOT_AVATAR):
            message_placeholder = st.empty()
            response = index.search(query_text=prompt)
            if response and response[0].metadata.get("video_id"):
                video_id = response[0].metadata["video_id"]
                transcript = response[0].metadata.get("transcript", "")
                YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # Define the API key
                video_title = get_youtube_video_title(video_id, YOUTUBE_API_KEY)
                FULL_RESPONSE = f"Found video: {video_title}"
                st.session_state["video_id"] = video_id
                st.session_state["transcript"] = transcript
            else:
                FULL_RESPONSE = "No relevant video found."

            message_placeholder.markdown(FULL_RESPONSE)
            st.session_state.messages.append(
                {"role": "assistant", "content": FULL_RESPONSE}
            )

# Dialogue extraction interface
if "video_id" in st.session_state:
    if dialogue := st.chat_input(
        "Enter the specific dialogue you're looking for:", key="dialogue_search"
    ):
        st.session_state.messages.append({"role": "user", "content": dialogue})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(dialogue)

        with st.chat_message("assistant", avatar=BOT_AVATAR):
            transcript = st.session_state.get("transcript", "[]")
            result = find_matching_dialogue(transcript, st.session_state["video_id"], dialogue)
            st.write(result)
            st.session_state.messages.append({"role": "assistant", "content": result})

# Save chat history after each interaction
save_chat_history(st.session_state.messages)
