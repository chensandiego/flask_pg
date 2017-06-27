import feedparser
import json
import codecs
import urllib.parse
import requests
import datetime
from urllib.request import urlopen
from flask import Flask,render_template
from flask import request,make_response

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir)))
import api






app=Flask(__name__)

RSS_FEEDS={
    'bbc':'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn':'http://rss.cnn.com/rss/edition.rss',
    'fox':'http://feeds.foxnews.com/foxnews/latest',
    'iol':'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS={'publication':'bbc','city':'London,UK','currency_from':'GBP','currency_to':'USD'}


def get_value_with_fallback(key):
    print("my key"+key)
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]


@app.route("/")
def home():
    #get customized headlines,based on user input or default
    publication=get_value_with_fallback('publication')
    articles=get_news(publication)

    #get customized weather based on user input or default

    city= get_value_with_fallback('city')

    weather=get_weather(city)
    

    #get customized currency based on user input or default
    currency_from=get_value_with_fallback("currency_from")
    currency_to=get_value_with_fallback("currency_to")

    rate,currencies=get_rate(currency_from,currency_to)


    # SAVE COOKIES AND return TEMPLATE
    response = make_response(render_template("home.html",
    articles=articles,
    weather=weather,
    currency_from=currency_from,
    currency_to=currency_to,
    rate=rate,
    currencies=sorted(currencies)))

    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication",publication,expires=expires)
    response.set_cookie("city",city,expires=expires)
    response.set_cookie("currency_from",currency_from,expires=expires)
    response.set_cookie("currency_to",currency_to,expires=expires)

    return response


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication=DEFAULTS["publication"]
    else:
        publication=query.lower()
    feed=feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']
    #get weahter info by pass location to get_weather



def get_weather(query):
    api_url='http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid='+api.api_key
    query=urllib.parse.quote(query)

    url=api_url.format(query)

    data=urlopen(url).read()
    parsed=requests.get(url).json()

#    parsed=json.loads(data)
    weather=None
    if parsed.get("weather"):

        weather={"description":parsed["weather"][0]["description"],"temperature":parsed["main"]["temp"],"city":parsed["name"],'country':parsed['sys']['country']}
    print (weather)
    return weather


def get_rate(frm,to):
    currency_url="https://openexchangerates.org/api/latest.json?app_id="+api.openexchange_api
    all_currency=urlopen(currency_url).read()
    parsed=requests.get(currency_url).json().get('rates')

    frm_rate=parsed.get(frm.upper())
    to_rate=parsed.get(to.upper())
    return (to_rate/frm_rate,parsed.keys())


if __name__=="__main__":
    app.run(debug=True)
