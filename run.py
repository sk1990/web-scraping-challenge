import pymongo
from flask import Flask, render_template, url_for

import os

import numpy as np
import pandas as pd

import requests
from bs4 import BeautifulSoup

from twitter_scraper import get_tweets


def scrape_news():
    URL = "https://mars.nasa.gov/news/"
    res = requests.get(URL)
    soup = BeautifulSoup(res.content, 'html.parser')

    headings = soup.find_all('div', class_='content_title')
    desciptions = soup.find_all('div', class_="rollover_description_inner")
    images = soup.find_all('img', class_="img-lazy")

    news = []

    for i in range( len(headings) ):
        news.append( [headings[0].text, desciptions[0].text, images[0].get('data-lazy')] )

    return news


def mars_facts_html():
    URL = "https://space-facts.com/mars/"

    tables = pd.read_html(URL)
    df = tables[0]
    df.columns = ['Property', 'Value']
    
    return df.to_html()


def mars_hemisphere():
    URL = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

    res = requests.get(URL)
    soup = BeautifulSoup(res.content, 'html.parser')

    link_names = list()
    links = soup.find_all('h3')

    for link in links:
        link_names.append(link.text)
        
    links = {}
    temp = soup.find_all('a', class_="itemLink product-item")

    for i in range(4):
        links[ link_names[i] ] = "https://astrogeology.usgs.gov" + temp[i].get("href")

    return links


def twitter_news():
    for tweet in get_tweets('marswxreport', pages=1):
        latest = tweet['text']
        return latest

def scrape_():
    news = scrape_news()
    facts = mars_facts_html()
    hemi = mars_hemisphere()
    t_new = twitter_news()
    mars = {
        "news": news,
        "facts": facts,
        "hemi": hemi,
        'twit': t_new
    }
    return mars

URI = 'mongodb://localhost:27017/mission_to_mars'
client = pymongo.MongoClient(URI)

app = Flask(__name__)

@app.route("/")
def index():
    mars = client.db.mars1.find_one()
    print (mars)
    for i in mars:
        print (mars[i])
    return render_template("index.html", mars=mars)

@app.route("/scrape")
def scrape():
    mars = client.db.mars1
    mars_data = scrape_()
    mars.insert_one(mars_data)
    print (mars)
    return url_for('index')

if __name__ == "__main__":
    app.run(debug=True)