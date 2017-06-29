from dbhelper import DBHelper
from flask import Flask
from flask import render_template
from flask import request
import dbconfig
import json
import datetime
import dateparser
import string

app = Flask(__name__)

DB = DBHelper()

categories=['mugging','break-in']
error_message=''
@app.route("/")
def home():
    crimes = DB.get_all_crimes()
    crimes = json.dumps(crimes)
    return render_template("home.html",crimes=crimes,categories=categories,error_message=error_message,gkey=dbconfig.google_key)


@app.route("/submitcrime",methods=["POST"])
def submitcrime():
    category=request.form.get("category")
    if category not in categories:
        return home()
    date = format_date(request.form.get("date"))
    if not date:
        return home("invalid date, please use yyyy-mm-dd format")

    try:
        latitude=float(request.form.get("latitude"))
        longitude=float(request.form.get("longitude"))
    except ValueError:
        return home()
    description=request.form.get("description")
    DB.add_crime(category,date,latitude,longitude,description)
    return home()

def format_date(userdate):
    date=dateparser.parse(userdate)
    try:
        return datetime.datetime.strftime(date,"%Y-%m-%d")
    except TypeError:
        return None

def sanitize_string(userinput):
    whitelist=string.ascii_letters + string.digits + " !?$.,:-'()&'"
    return filter(lambda x: x in whitelist,userinput)

@app.route("/clear")
def clear():
    try:
        DB.clear_all()
    except Exception as e:
        print (e)
    return home()

if __name__ == '__main__':
    app.run(debug=True)
