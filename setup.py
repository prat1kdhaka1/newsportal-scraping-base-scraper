from setuptools import setup, find_packages

setup(
    name="newscraper",
    version="1.0",
    packages=find_packages(),
    entry_points={"scrapy": ["settings = newscraper.settings"]},
)
