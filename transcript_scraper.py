import requests
import json
import os
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

# Define database and JSON file paths
DB_PATH = "video_data.db"
JSON_PATH = "video_transcripts.json"

# Define the URL
URL = (
    'https://mssp-scraper.vercel.app/video_data.json?sql=with%20most_recent_video%20as%20('
    '%0D%0A%20%20select%0D%0A%20%20%20%20id%0D%0A%20%20from%0D%0A%20%20%20%20videos%0D%0A'
    '%20%20order%20by%0D%0A%20%20%20%20snippet_publishedAt%20desc%0D%0A%20%20limit%0D%0A'
    '%20%20%20%201%0D%0A)%2C%20missing_transcripts%20as%20(%0D%0A%20%20select%0D%0A%20%20%20'
    '%20id%0D%0A%20%20from%0D%0A%20%20%20%20transcripts%0D%0A%20%20where%0D%0A%20%20%20%20'
    'transcript%20is%20null%0D%0A)%0D%0Aselect%0D%0A%20%20*%0D%0Afrom%0D%0A%20%20most_recent_video'
    '%0D%0Aunion%0D%0Aselect%0D%0A%20%20*%0D%0Afrom%0D%0A%20%20missing_transcripts'
)

def fetch_video_ids():
    response = requests.get(URL)
    return [item[0] for item in response.json()['rows']]

def fetch_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text_only = ' '.join([segment['text'].replace('[\u00a0__\u00a0]', '[EXPLICIT]') for segment in transcript_list])
        return transcript_text_only
    except TranscriptsDisabled:
        return None

def save_transcripts(video_transcripts):
    with open(JSON_PATH, 'w') as f:
        json.dump(video_transcripts, f)

def fetch_video_details():
    video_ids = fetch_video_ids()
    video_transcripts = [{'id': video_id, 'transcript': fetch_transcript(video_id)} for video_id in video_ids]
    save_transcripts(video_transcripts)

if __name__ == "__main__":
    fetch_video_details()
    command = ['sqlite-utils', 'upsert', DB_PATH, 'transcripts', JSON_PATH, '--pk', 'id']
    subprocess.run(command, check=True)
