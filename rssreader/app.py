import feedparser
import json
import codecs
import urllib.parse
import requests
from urllib.request import urlopen
from flask import Flask,render_template
from flask import request
from api import api_key,openexchange_api

app=Flask(__name__)

RSS_FEEDS={
    'bbc':'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn':'http://rss.cnn.com/rss/edition.rss',
    'fox':'http://feeds.foxnews.com/foxnews/latest',
    'iol':'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS={'publication':'bbc','city':'London,UK','currency_from':'GBP','currency_to':'USD'}

@app.route("/")
def home():
    #get customized headlines,based on user input or default
    publication=request.args.get('publication')
    if not publication:
        publication=DEFAULTS['publication']
    articles=get_news(publication)

    #get customized weather based on user input or default
    city= request.args.get('city')
    if not city:
        city=DEFAULTS['city']

    weather=get_weather(city)


    #get customized currency based on user input or default
    currency_from=request.args.get("currency_from")
    if not currency_from:
        currency_from=DEFAULTS['currency_from']
    currency_to=request.args.get("currency_to")
    if not currency_to:
        currency_to=DEFAULTS['currency_to']

    rate,currencies=get_rate(currency_from,currency_to)


    return render_template("home.html",articles=articles,weather=weather,currency_from=currency_from,currency_to=currency_to,rate=rate,currencies=sorted(currencies))


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication=DEFAULTS["publication"]
    else:
        publication=query.lower()
    feed=feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']
    #get weahter info by pass location to get_weather



def get_weather(query):
    api_url='http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid='+api_key
    query=urllib.parse.quote(query)
    url=api_url.format(query)
    data=urlopen(url).read()
    parsed=requests.get(url).json()

#    parsed=json.loads(data)
    weather=None
    if parsed.get("weather"):

        weather={"description":parsed["weather"][0]["description"],"temperature":parsed["main"]["temp"],"city":parsed["name"],'country':parsed['sys']['country']}

    return weather


def get_rate(frm,to):
    currency_url="https://openexchangerates.org/api/latest.json?app_id="+openexchange_api
    all_currency=urlopen(currency_url).read()
    parsed=requests.get(currency_url).json().get('rates')

    frm_rate=parsed.get(frm.upper())
    to_rate=parsed.get(to.upper())
    return (to_rate/frm_rate,parsed.keys())


if __name__=="__main__":
    app.run(debug=True)
