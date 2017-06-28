from dbhelper import DBHelper

from flask import Flask
from flask import render_template

from flask import request
import dbconfig

app = Flask(__name__)

DB = DBHelper()


@app.route("/")
def home():
    try:
        data = DB.get_all_input()
    except Exception as e:
        print (e)
        data = None
    return render_template("home.html",data=data,gkey=dbconfig.google_key)


@app.route("/submitcrime",methods=["POST"])
def submitcrime():
    category=request.form.get("category")
    date = request.form.get("date")
    latitude=float(request.form.get("latitude"))
    longitude=float(request.form.get("longitude"))
    description=request.form.get("description")
    DB.add_crime(category,date,latitude,longitude,description)
    return home()


@app.route("/clear")
def clear():
    try:
        DB.clear_all()
    except Exception as e:
        print (e)
    return home()

if __name__ == '__main__':
    app.run(debug=True)
