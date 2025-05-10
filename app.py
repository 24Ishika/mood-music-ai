import streamlit as st
import sqlite3  # Import SQLite3
from transformers import pipeline
from googleapiclient.discovery import build

# Set up Streamlit UI
st.set_page_config(page_title="Mood Detection Bot", layout="centered")
st.title("💬 MindTune: AI-Based Mood Detection ")
st.write("Type a message, and I'll analyze your mood!")

# Initialize chat history if not present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Load sentiment analysis model
@st.cache_resource
def load_model():
    return pipeline("sentiment-analysis")

sentiment_analyzer = load_model()

# Function to create the database and table (if not exists)
def create_database():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            detected_mood TEXT,
            confidence_score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

create_database()  # Ensure the database is set up on startup

# Function to save chat history in the database
def save_chat_history(user_message, detected_mood, confidence_score):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO chat_history (user_message, detected_mood, confidence_score)
        VALUES (?, ?, ?)
    ''', (user_message, detected_mood, confidence_score))

    conn.commit()
    conn.close()

# Function to load previous chat history
def load_chat_history():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_message, detected_mood, confidence_score FROM chat_history ORDER BY timestamp ASC")
    chat_history = cursor.fetchall()

    conn.close()
    return chat_history

# Load and display previous chat messages from the database
if not st.session_state.messages:
    chat_data = load_chat_history()
    for user_msg, mood, score in chat_data:
        st.session_state.messages.append({
            "role": "user",
            "avatar": "🧑",
            "text": f"{user_msg} (Mood: {mood}, Confidence: {score:.2f})"
        })

# Function to fetch YouTube videos based on mood
YOUTUBE_API_KEY = "AIzaSyAMhVwEWYsQlBLVSPYUDsomyWzBCXyWeh4"  # Replace with your actual API key

def fetch_youtube_videos(mood):
    """Fetch top 3 YouTube videos based on the detected mood."""
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    
    search_query = f"{mood} subliminal music relaxation"
    
    request = youtube.search().list(
        part="snippet",
        q=search_query,
        maxResults=3,
        type="video"
    )
    
    response = request.execute()
    
    video_links = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        video_links.append(f"[{title}](https://www.youtube.com/watch?v={video_id})")

    return video_links

# Display all previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message["avatar"]):
        st.markdown(message["text"])

if st.button("🗑 Clear Chat"):
    st.session_state.messages = []  # Clear session state messages
    st.rerun()  # Refresh the UI

# User input
user_input = st.chat_input("Type your message...")

if user_input:
    # Immediately display user message
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)
    
    # Store user message in session state
    st.session_state.messages.append({"role": "user", "avatar": "🧑", "text": user_input})

    # Perform sentiment analysis
    result = sentiment_analyzer(user_input)[0]
    mood = result['label']
    score = result['score']

    # Fetch YouTube video recommendations
    video_links = fetch_youtube_videos(mood)

    # Determine AI response
    if mood == "POSITIVE":
        response = f"😊 Your mood seems positive! (Confidence: {score:.2f})"
    elif mood == "NEGATIVE":
        response = f"😞 You seem to be in a negative mood. (Confidence: {score:.2f})"
    else:
        response = f"😐 Your mood appears neutral. (Confidence: {score:.2f})"

    # Add YouTube video links to response
    response += "\n\n🎵 Here are some subliminal videos for you:\n"
    response += "\n".join(video_links)

    # Immediately display AI response
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(response)

    # Store AI response in session state
    st.session_state.messages.append({"role": "assistant", "avatar": "🤖", "text": response})

    # Save chat history in database
    save_chat_history(user_input, mood, score)
