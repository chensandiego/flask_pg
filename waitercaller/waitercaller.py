from flask import Flask,render_template
from flask.ext.login import LoginManager
from flask.ext.login import login_required
from flask.ext.login import login_user,logout_user
from flask.ext.login import current_user

from flask import redirect
from flask import url_for
from flask import request


import config,datetime
if config.test:
    from mockdbhelper import MockDBHelper as DBHelper
else:
    from dbhelper import DBHelper
from passwordhelper import PasswordHelper
from bitlyhelper import BitlyHelper
from forms import RegistrationForm,LoginForm,CreateTableForm
from user import User

DB=DBHelper()
PH=PasswordHelper()
BH =BitlyHelper()

app = Flask(__name__)
app.secret_key='afalksdf4n3400assslxxxj'
login_manager=LoginManager(app)
@app.route("/")
def home():
#    registrationform=RegistrationForm()
    return render_template("home.html",loginform=LoginForm(),registrationform=RegistrationForm())


@app.route("/register",methods=["POST"])
def register():
    form=RegistrationForm(request.form)
    if form.validate():
        if DB.get_user(form.email.data):
            form.email.errors.append("Email has already registered")
            return render_template('home.html',loginform=LoginForm(),registrationform=form)
        salt=PH.get_salt()

        if type(salt)!=str:
            salt=salt.decode("utf-8")

        hashed =PH.get_hash(form.password2.data + salt)
        DB.add_user(form.email.data,salt,hashed)
        return render_template("home.html",loginform=LoginForm(),registrationform=form,onloadmessage="Registration successful. Please login")

    return render_template("home.html",registrationform=form,loginform=LoginForm())
@app.route("/login",methods=["POST"])
def login():
    form = LoginForm(request.form)
    if form.validate():
        stored_user=DB.get_user(form.loginemail.data)
        if type(stored_user['salt']) != str:
            stored_user['salt']=stored_user['salt'].decode("utf-8")

        if stored_user and PH.validate_password(form.loginpassword.data,stored_user['salt'],stored_user['hashed']):
            user=User(form.loginemail.data)
            login_user(user,remember=True)
            return redirect(url_for('account'))
        form.loginemail.errors.append("email or password invalid")
    return render_template("home.html",loginform=form,registrationform=RegistrationForm())
#    if type(stored_user['salt']) != str:
#        stored_user['salt']=stored_user['salt'].decode("utf-8")
        #user=User(email)
        #login_user(user,remember=True)

#    return home()


@app.route("/dashboard")
@login_required
def dashboard():
    now = datetime.datetime.now()
    requests=DB.get_requests(current_user.get_id())
    for req in requests:
        deltaseconds=(now - req['time']).seconds
        req['wait_minutes']="{}.{}".format((deltaseconds/60),str(deltaseconds % 60).zfill(2))

    return render_template("dashboard.html",requests=requests)


@app.route("/dashboard/resolve")
@login_required
def dashboard_resolve():
    request_id=request.args.get("request_id")
    DB.delete_request(request_id)
    return redirect(url_for('dashboard'))

@app.route("/account")
@login_required
def account():
    tables=DB.get_tables(current_user.get_id())

    return render_template("account.html",createtableform=CreateTableForm(),tables=tables)

@app.route("/account/createtable", methods=["POST"])
@login_required
def account_createtable():
    form = CreateTableForm(request.form)
    if form.validate():
        tableid=DB.add_table(form.tablenumber.data,current_user.get_id())
        new_url=BH.shorten_url(config.base_url + "newrequest/"+str(tableid))
        DB.update_table(tableid,new_url)
        return redirect(url_for('account'))
    return render_template("account.html",createtableform=form,tables=DB.get_tables(current_user.get_id()))

@app.route("/newrequest/<tid>")
def new_request(tid):
    DB.add_request(tid,datetime.datetime.now())
    return "Your request has been logged and a waiter will be with you shortly"


@app.route("/account/deletetable")
@login_required
def account_deletetable():
    tableid=request.args.get("tableid")
    DB.delete_table(tableid)
    return redirect(url_for('account'))


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
