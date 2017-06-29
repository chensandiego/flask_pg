from flask import Flask,render_template
from flask.ext.login import LoginManager
from flask.ext.login import login_required
from flask.ext.login import login_user,logout_user
from flask import redirect
from flask import url_for
from flask import request



from mockdbhelper import MockDBHelper as DBHelper
from passwordhelper import PasswordHelper
from user import User

DB=DBHelper()
PH=PasswordHelper()

app = Flask(__name__)
app.secret_key='afalksdf4n3400assslxxxj'
login_manager=LoginManager(app)
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register",methods=["POST"])
def register():
    email=request.form.get("email")
    pw1=request.form.get("password")
    pw2=request.form.get("password2")
    if not pw1 == pw2:
        return redirect(url_for('home'))
    if DB.get_user(email):
        return redirect(url_for('home'))
    salt=PH.get_salt()
    hashed = PH.get_hash(pw1+salt.decode("utf-8"))
    DB.add_user(email,salt,hashed)
    return redirect(url_for('home'))
@app.route("/login",methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    stored_user=DB.get_user(email)
    if type(stored_user['salt']) != str:
        stored_user['salt']=stored_user['salt'].decode("utf-8")
    if stored_user and PH.validate_password(password,stored_user['salt'],stored_user['hashed']):
        user=User(email)
        login_user(user,remember=True)
        return redirect(url_for('account'))
    return home()

@app.route("/account")
@login_required
def account():
    return "you ar ein"


@login_manager.user_loader
def load_user(user_id):
    user_password=DB.get_user(user_id)
    if user_password:
        return User(user_id)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__=='__main__':
    app.run(debug=True)
