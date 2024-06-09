import streamlit as st
import os
import shelve
from trufflepig import Trufflepig
from dotenv import load_dotenv
from utils import get_youtube_video_title, find_matching_dialogue

# Load environment variables
load_dotenv()

# Streamlit title
st.title("Beast Search")

# Constants for avatars
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# Initialize Trufflepig client
client = Trufflepig(os.getenv('TRUFFLE_PIG_KEY'))
index = client.get_index('MrBeastYouTube')

# Load chat history from shelve file
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

# Save chat history to shelve file
def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

# Function to reset video search
def reset_video_search():
    if 'video_id' in st.session_state:
        del st.session_state['video_id']
    if 'transcript' in st.session_state:
        del st.session_state['transcript']

# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Sidebar with a button to delete chat history
with st.sidebar:
    if st.button("Delete Chat History"):
        st.session_state.messages = []
        save_chat_history([])

    # Button to initiate new video search, now correctly placed with defined function above
    if st.button("New Video Search"):
        reset_video_search()

# Display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Main chat interface
if 'video_id' not in st.session_state:
    if prompt := st.chat_input("Enter your video query:", key="video_query"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)

        # Search for video
        with st.chat_message("assistant", avatar=BOT_AVATAR):
            message_placeholder = st.empty()
            response = index.search(query_text=prompt)
            if response and response[0].metadata.get('video_id'):
                video_id = response[0].metadata['video_id']
                transcript = response[0].metadata.get('transcript', '')  # Get transcript if available
                video_title = get_youtube_video_title(video_id, YOUTUBE_API_KEY)
                full_response = f"Found video: {video_title}"
                st.session_state['video_id'] = video_id  # Store video ID in session
                st.session_state['transcript'] = transcript  # Store transcript in session
            else:
                full_response = "No relevant video found."
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

# Dialogue extraction interface
if 'video_id' in st.session_state:
    if dialogue := st.chat_input("Enter the specific dialogue you're looking for:", key="dialogue_search"):
        st.session_state.messages.append({"role": "user", "content": dialogue})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(dialogue)

        # Find matching dialogue
        with st.chat_message("assistant", avatar=BOT_AVATAR):
            transcript = st.session_state.get('transcript', '[]')
            result = find_matching_dialogue(transcript, st.session_state['video_id'], dialogue)
            st.write(result)
            st.session_state.messages.append({"role": "assistant", "content": result})

# Save chat history after each interaction
save_chat_history(st.session_state.messages)
