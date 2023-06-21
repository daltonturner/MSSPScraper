# MSSPScraper
[![Run Scraper](https://github.com/daltonturner/MSSPScraper/actions/workflows/main.yml/badge.svg)](https://github.com/daltonturner/MSSPScraper/actions/workflows/main.yml) [![Extract Transcripts](https://github.com/daltonturner/MSSPScraper/actions/workflows/extract_transcripts.yml/badge.svg)](https://github.com/daltonturner/MSSPScraper/actions/workflows/extract_transcripts.yml)

Uses the YouTube API to scrape video data from Matt And Shane's Secret Podcast YouTube uploads. Check out some formatted data [here](https://mssp-scraper.vercel.app/video_data?sql=select%0D%0A++v.id%2C%0D%0A++v.snippet_publishedAt%2C%0D%0A++v.statistics_viewCount%2C%0D%0A++v.statistics_likeCount%2C%0D%0A++v.statistics_commentCount%2C%0D%0A++v.snippet_title%2C%0D%0A++v.snippet_description%2C%0D%0A++t.transcript%2C%0D%0A++v.snippet_thumbnails_maxres_url%0D%0Afrom%0D%0A++videos+as+v%0D%0A++left+join+transcripts+as+t+on+t.id+%3D+v.id%0D%0Aorder+by%0D%0A++v.snippet_publishedAt+desc&_hide_sql=1), or check out the raw tables [here](https://mssp-scraper.vercel.app/). 

<p align="center"><img src="https://i.ytimg.com/vi/Kq_0QgzLS8o/maxresdefault.jpg" alt="Most recent thumbnail" max-width="500px" max-height="500px"></p>
