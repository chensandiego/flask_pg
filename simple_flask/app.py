from flask import Flask,render_template,flash,request
from wtforms import Form,TextField,TextAreaField,validators,StringField,SubmitField

app= Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class ResuableForm(Form):
    name = TextField('Name:',validators=[validators.required()])


@app.route("/",methods=['GET','POST'])
def hello():
    form = ResuableForm(request.form)

    print (form.errors)
    if request.method == 'POST':
        name=request.form['name']
        print (name)

        if form.validate():
            flash('hello'+name)
        else:
            flash('all the form field are needed')
    return render_template('hello.html',form=form)

if __name__=='__main__':
    app.run()
