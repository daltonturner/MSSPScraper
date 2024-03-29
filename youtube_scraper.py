import requests
import time
import json
import os
from sqlite_utils import Database

class YouTubeScraper:
    def __init__(self, api_key, channel_id, uploads_id, data_filename):
        self.api_key = api_key
        self.channel_id = channel_id
        self.uploads_id = uploads_id
        self.data_filename = data_filename
        self.video_links = []
        self.video_details = []

    def execute_scraper(self):
        """
        Execute the scraping process by fetching video links and details, then saving them to files.
        """
        self.fetch_video_links()
        self.save_to_file(self.video_links, 'video_links.json')
        self.fetch_video_details()
        self.save_to_file(self.video_details, 'video_data.json')

    def fetch_video_details(self):
        """
        Fetch the details of each video using the YouTube API.
        """
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

    def fetch_video_links(self):
        """
        Fetch the links of each video in the channel using the YouTube API.
        """
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

    def interact_with_database(self, db):
        """
        Interact with the database by upserting video details and links, and creating a summarized data table.
        """
        db["videos"].upsert_all(self.video_details, pk="id", alter=True)
        db["video_links"].upsert_all(self.video_links, pk="id", alter=True)

        db.execute("DROP TABLE IF EXISTS summarized_data")
        db.execute("""
            CREATE TABLE summarized_data AS
            SELECT v.id, 
            v.snippet_title, 
            v.snippet_publishedAt, 
            v.snippet_description, 
            v.snippet_thumbnails_maxres_url, 
            v.statistics_viewCount,
            v.statistics_likeCount,
            v.statistics_commentCount,
            v.contentDetails_regionRestriction_blocked,
            vl.url
            FROM videos AS v 
            JOIN video_links AS vl ON v.id = vl.id
        """)

    def save_to_file(self, data, filename):
        """
        Save the given data to a file with the given filename.
        """
        with open(filename, 'w') as f:
            json.dump(data, f)

if __name__ == "__main__":
    api_key = os.environ["YOUTUBE_API_KEY"]
    channel_id = "UC4fZeoNxAXfbIpT3swsVh9w"
    uploads_id = "UU4fZeoNxAXfbIpT3swsVh9w"
    data_filename = "video_data.json"

    scraper = YouTubeScraper(api_key, channel_id, uploads_id, data_filename)
    scraper.execute_scraper()

    db = Database("video_data.db")
    scraper.interact_with_database(db)
