"""
Module for searching and processing YouTube video titles and dialogues.
"""

import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast


def get_youtube_video_title(video_id, api_key):
    """
    Fetches the title of a YouTube video using the YouTube Data API.

    Parameters:
        video_id (str): YouTube video ID.
        api_key (str): API key for accessing YouTube Data API.

    Returns:
        str: Title of the video or an error message.
    """
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}"
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        data = response.json()
        return data["items"][0]["snippet"]["title"] if "items" in data and data["items"] else "Video not found"
    return f"Failed to fetch data: {response.status_code}"


def find_matching_dialogue(transcript_list, video_id, key_phrase, window_size=3):
    """
    Finds and returns the segment of video dialogue that best matches a given key phrase.

    Parameters:
        transcript_list (str): A string representation of a list containing transcript entries with text, start, and duration.
        video_id (str): YouTube video ID.
        key_phrase (str): Phrase to match in the transcript.
        window_size (int): Number of consecutive entries to consider in each segment for matching.

    Returns:
        str: Description of the best matching dialogue segment and a URL to the timestamp in the video.
    """
    # Convert string representation of list into actual list
    try:
        transcript_list = ast.literal_eval(transcript_list)
        texts = [entry["text"] for entry in transcript_list]
        segments = []

        # Create segments
        for i in range(len(texts) - window_size + 1):
            segment_text = " ".join(texts[i:i + window_size])
            start_time = transcript_list[i]["start"]
            end_time = transcript_list[i + window_size - 1]["start"] + transcript_list[i + window_size - 1]["duration"]
            segments.append((segment_text, start_time, end_time))

        # Vectorization and similarity calculation
        segment_texts = [segment[0] for segment in segments] + [key_phrase]
        vectorizer = TfidfVectorizer().fit(segment_texts)
        vectors = vectorizer.transform(segment_texts)
        similarities = cosine_similarity(vectors[-1], vectors[:-1]).flatten()
        most_similar_index = similarities.argmax()
        best_match = segments[most_similar_index]

        # Create URL for the video at the specific time
        url = f"https://www.youtube.com/watch?v={video_id}&t={int(best_match[1])}s"
        return f'We found "{best_match[0]}" at {url}'
    except Exception as e:
        return "We could not locate that clip."