import naive_bayes
from setuptools import setup

setup(
    name="hackernews-recommendations",
    version="0.2.0",
    description="A simple HackerNews recommendation system",
    author="Shaorrran",
    author_email="",
    packages=["naive_bayes"],
    entry_points={"console_scripts": []},
    url="",
    license="WTFPL",  # it's a real license, look it up
    python_requires=">=3.8.0",
)
