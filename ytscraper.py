import requests
import time
import json
import os
import subprocess

api_key = os.environ["YOUTUBE_API_KEY"]
channel_id = "UC4fZeoNxAXfbIpT3swsVh9w"
uploads_id = "UU4fZeoNxAXfbIpT3swsVh9w"
data_filename = "video_data.json"

# Get the uploads playlist ID (for reference)
# channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={api_key}"
# response = requests.get(channel_url).json()
# uploads_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

def fetch_video_details(api_key, channel_id, uploads_id, data_filename):
    # Get the videos in the playlist
    video_links = []
    base_url = 'https://www.googleapis.com/youtube/v3/playlistItems?'
    first_url = f'{base_url}part=snippet%2CcontentDetails&maxResults=50&playlistId={uploads_id}&key={api_key}'

    url = first_url
    while True:
        inp = requests.get(url)
        resp = inp.json()
        
        for item in resp['items']:
            video_links.append(item['contentDetails']['videoId'])

        next_page_token = resp.get('nextPageToken')
        if next_page_token:
            url = first_url + '&pageToken=' + next_page_token
        else:
            break

        time.sleep(1)  # To respect the YouTube API rate limit

    # Load the old video data, if it exists
    if os.path.exists(data_filename):
        with open(data_filename, 'r') as f:
            old_video_data = json.load(f)
    else:
        old_video_data = []

    # Get the old video IDs
    old_video_ids = [video['id'] for video in old_video_data]

    # Get the details for each new video
    video_details = old_video_data.copy()
    base_url = 'https://www.googleapis.com/youtube/v3/videos?'

    for video_id in video_links:
        # Skip if we already have data for this video
        if video_id in old_video_ids:
            continue

        video_url = f'{base_url}part=snippet,statistics,contentDetails&id={video_id}&key={api_key}'
        response = requests.get(video_url).json()
        video_details.append(response['items'][0])

        time.sleep(1)  # To respect the YouTube API rate limit

    # Save the data to a file
    with open(data_filename, 'w') as f:
        json.dump(video_details, f)

if __name__ == "__main__":
    fetch_video_details(api_key, channel_id, uploads_id, data_filename)

    # Now use subprocess to call sqlite-utils
    command = ['sqlite-utils', 'upsert', 'video_data.db', 'videos', data_filename, '--pk=id', '--flatten', '--alter']
    subprocess.run(command, check=True)
