import requests
import json

def inject_image_link(md_file_path):
    # Make a GET request to the Deployed Datasette URL
    response = requests.get("https://mssp-scraper.vercel.app/video_data.json?sql=select%0D%0A%20%20snippet_thumbnails_maxres_url%0D%0Afrom%0D%0A%20%20videos%0D%0Aorder%20by%0D%0A%20%20snippet_publishedAt%20desc%0D%0Alimit%20%0D%0A%20%201")

    # Parse the JSON response
    data = response.json()

    # Access the URL
    image_link = data["rows"][0][0]

    # Define the HTML string for the image
    image_html = f'<p align="center"><img src="{image_link}" alt="Most recent thumbnail" max-width="500px" max-height="500px"></p>\n'

    # Read the original markdown file
    with open(md_file_path, 'r') as file:
        original_content = file.read()

    # Add the image link to the bottom of the markdown file
    new_content = original_content + "\n" + image_html

    # Write the new content back to the markdown file
    with open(md_file_path, 'w') as file:
        file.write(new_content)

if __name__ == "__main__":
    # Example usage
    inject_image_link('README.md')
