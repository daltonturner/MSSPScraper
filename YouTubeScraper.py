import requests
import time
import json
import os
import subprocess

class YouTubeScraper:
    def __init__(self, api_key, channel_id, uploads_id, data_filename):
        self.api_key = api_key
        self.channel_id = channel_id
        self.uploads_id = uploads_id
        self.data_filename = data_filename
        self.video_links = []
        self.video_details = []

    def fetch_video_links(self):
        base_url = 'https://www.googleapis.com/youtube/v3/playlistItems?'
        first_url = f'{base_url}part=snippet%2CcontentDetails&maxResults=50&playlistId={self.uploads_id}&key={self.api_key}'

        url = first_url
        while True:
            try:
                resp = requests.get(url).json()
                for item in resp['items']:
                    video_id = item['contentDetails']['videoId']
                    video_url = f'https://www.youtube.com/watch?v={video_id}'
                    self.video_links.append({'id': video_id, 'url': video_url})

                next_page_token = resp.get('nextPageToken')
                if next_page_token:
                    url = first_url + '&pageToken=' + next_page_token
                else:
                    break

                time.sleep(1)  # To respect the YouTube API rate limit
            except Exception as e:
                print(f"An error occurred: {e}")
                break

    def fetch_video_details(self):
        base_url = 'https://www.googleapis.com/youtube/v3/videos?'
        for video in self.video_links:
            video_id = video['id']  # Get the video ID from the dictionary
            try:
                video_url = f'{base_url}part=snippet,statistics,contentDetails&id={video_id}&key={self.api_key}'
                response = requests.get(video_url).json()
                self.video_details.append(response['items'][0])

                time.sleep(1)  # To respect the YouTube API rate limit
            except Exception as e:
                print(f"An error occurred: {e}")

    def save_to_file(self, data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f)

if __name__ == "__main__":
    api_key = os.environ["YOUTUBE_API_KEY"]
    channel_id = "UC4fZeoNxAXfbIpT3swsVh9w"
    uploads_id = "UU4fZeoNxAXfbIpT3swsVh9w"
    data_filename = "video_data.json"

    scraper = YouTubeScraper(api_key, channel_id, uploads_id, data_filename)
    scraper.fetch_video_links()
    scraper.save_to_file(scraper.video_links, 'video_links.json')
    scraper.fetch_video_details()
    scraper.save_to_file(scraper.video_details, 'video_data.json')

    # Now use subprocess to call sqlite-utils
    command = ['sqlite-utils', 'upsert', 'video_data.db', 'videos', 'video_data.json', '--pk=id', '--flatten', '--alter']
    subprocess.run(command, check=True)
    command = ['sqlite-utils', 'upsert', 'video_data.db', 'video_links', 'video_links.json', '--pk=id', '--flatten', '--alter']
    subprocess.run(command, check=True)