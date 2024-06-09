import requests
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast

def get_youtube_video_title(video_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            return data['items'][0]['snippet']['title']
        else:
            return "Video not found"
    else:
        return f"Failed to fetch data: {response.status_code}"

def find_matching_dialogue(transcript_list, video_id, key_phrase, window_size=3):
    # Extract texts from the transcript list
    transcript_list = ast.literal_eval(transcript_list)
    texts = [entry['text'] for entry in transcript_list]

    # Create overlapping segments with start and end times
    segments = []
    for i in range(len(texts) - window_size + 1):
        segment_text = ' '.join(texts[i:i + window_size])
        start_time = transcript_list[i]['start']
        end_time = transcript_list[i + window_size - 1]['start'] + transcript_list[i + window_size - 1]['duration']
        segments.append((segment_text, start_time, end_time))

    # Prepare the texts for TF-IDF vectorization
    segment_texts = [segment[0] for segment in segments]
    segment_texts.append(key_phrase)

    # Create a TF-IDF vectorizer and transform the texts
    vectorizer = TfidfVectorizer().fit(segment_texts)
    vectors = vectorizer.transform(segment_texts)

    # Compute the cosine similarity between the key phrase and all segment texts
    key_phrase_vector = vectors[-1]
    similarities = cosine_similarity(key_phrase_vector, vectors[:-1]).flatten()

    # Find the index of the most similar segment
    most_similar_index = similarities.argmax()

    # Return the most similar segment with start and end times
    best_match = segments[most_similar_index]

    url = f"https://www.youtube.com/watch?v={video_id}&t={int(best_match[1])}s"
    return f"We found \"{best_match[0]}\" at {url}"