import requests
import json
import os
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

# Define your database and JSON file paths
db_path = "video_data.db"
json_path = "video_transcripts.json"

def fetch_video_details():

    # Fetch video IDs from Datasette where transcript is None and the most recent video ID
    url = (
        'https://mssp-scraper.vercel.app/video_data.json?sql=with%20most_recent_video%20as%20('
        '%0D%0A%20%20select%0D%0A%20%20%20%20id%0D%0A%20%20from%0D%0A%20%20%20%20videos%0D%0A'
        '%20%20order%20by%0D%0A%20%20%20%20snippet_publishedAt%20desc%0D%0A%20%20limit%0D%0A'
        '%20%20%20%201%0D%0A)%2C%20missing_transcripts%20as%20(%0D%0A%20%20select%0D%0A%20%20%20'
        '%20id%0D%0A%20%20from%0D%0A%20%20%20%20transcripts%0D%0A%20%20where%0D%0A%20%20%20%20'
        'transcript%20is%20null%0D%0A)%0D%0Aselect%0D%0A%20%20*%0D%0Afrom%0D%0A%20%20most_recent_video'
        '%0D%0Aunion%0D%0Aselect%0D%0A%20%20*%0D%0Afrom%0D%0A%20%20missing_transcripts'
    )
    response = requests.get(url)
    video_ids = [item[0] for item in response.json()['rows']]

    # List to hold video transcript data
    video_transcripts = []

    # Fetch and store transcripts for each video
    for video_id in video_ids:
        try:
            # This call will try to get the manually created transcript first (if it exists)
            # If a manual transcript does not exist, it will fetch the automatically generated transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Extract only the 'text' field from each segment in the transcript list
            # Then join these text segments into a single string
            # Also replace '[\u00a0__\u00a0]' markers with '[EXPLICIT]'
            transcript_text_only = ' '.join([segment['text'].replace('[\u00a0__\u00a0]', '[EXPLICIT]') for segment in transcript_list])

            # Append the video ID and transcript text to the video_transcripts list
            video_transcripts.append({
                'id': video_id,
                'transcript': transcript_text_only
            })
        except TranscriptsDisabled:
            # If no transcript is available, append the video ID and None for the transcript
            video_transcripts.append({
                'id': video_id,
                'transcript': None
            })

    # Save the data to a file
    with open(json_path, 'w') as f:
        json.dump(video_transcripts, f)

if __name__ == "__main__":
    fetch_video_details()

    # Now use subprocess to call sqlite-utils
    command = ['sqlite-utils', 'upsert', db_path, 'transcripts', json_path, '--pk', 'id']
    subprocess.run(command, check=True)

