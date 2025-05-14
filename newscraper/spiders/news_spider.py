import scrapy
import json
import re
from urllib.parse import urljoin
import requests

class NewsSpiderSpider(scrapy.Spider):
    name = "news_spider"

    def __init__(self, job_data=None, base_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jobs = []
        self.base_url = base_url
        self.results = self.load_existing_articles()
        self.existing_urls = self.load_existing_urls()

        if job_data:
            try:
                self.jobs = json.loads(job_data)
            except json.JSONDecodeError:
                self.logger.error("Failed to decode job_data JSON")

    def load_existing_articles(self):
        try:
            filename = re.sub(r'[^a-zA-Z0-9]', "", self.base_url)
            filename = filename + ".json"
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def load_existing_urls(self):
        try:
            filename = re.sub(r'[^a-zA-Z0-9]', "", self.base_url)
            filename = filename + ".json"
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {article['url'] for article in data}
        except (FileNotFoundError, json.JSONDecodeError):
            return set()

    def start_requests(self):
        for job in self.jobs:
            url = job.get("category_url")
            url = urljoin(self.base_url, url)
            regex = job.get("regular_expression")
            # domain = job.get("domain")
            if url:
                self.logger.info(f"Starting with {url}")
                yield scrapy.Request(
                    url=url, callback=self.parse, meta={"base_url": self.base_url, "regex": regex}
                )

    def parse(self, response):
        base_url = response.meta.get("base_url")
        regex = response.meta.get("regex")
        pattern = re.compile(regex)
        a_tags = response.css("a::attr(href)").getall()
        for a_tag in a_tags:
            absolute_url = urljoin(base_url, a_tag)
            if pattern.match(absolute_url) and absolute_url not in self.existing_urls:
                yield scrapy.Request(
                url=absolute_url, callback=self.parse_article
            )       
        # Your logic here

    def parse_article(self, response):
        self.logger.info("#### Got the response")

        try:
            # Send content to the readability API
            api_response = requests.post(
            "http://172.19.128.1:3000/api/readability",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"htmlString": response.text})
        )

            if api_response.status_code == 200:
                json_data = api_response.json()
                json_data['url'] = response.url  # Include source URL
                self.results.append(json_data)
                filename = re.sub(r'[^a-zA-Z0-9]', "", self.base_url)
                filename = filename + ".json"
                with open(filename, 'a', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=4)
                    f.write(',\n')
            else:
                self.logger.error(f"API error for {response.url}: {api_response.status_code}")

        except Exception as e:
            self.logger.error(f"Exception occurred while processing article: {e}")

    def closed(self, reason):
        # Save results to a JSON file when spider finishes
        filename = re.sub(r'[^a-zA-Z0-9]', "", self.base_url)
        filename = filename + ".json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)
        self.logger.info(f"Saved {len(self.results)} articles to {filename}")