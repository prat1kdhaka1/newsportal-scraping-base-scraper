﻿# newsportal-scraping-base-scraper

## clone the repo and install requirements: `pip install -r requirements.txt`

## set the environment variables in the .env file

## run the command: `scrapyd`

## open another terminal and run: `scrapyd-deploy`


you can start the crawler by sending post request to localhost:6800/schedule.json with the following data:

{
    "project": "newscraper",
    "spider": "news_spider",
    "job_data": "[]",
    "base_url": "https://example.com"
}


job_data = [{"category_url": "https://www.example.com/category1", "regular_expression": "regex"}]
