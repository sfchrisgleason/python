# GleaAgg Client
#
# Requires Flask and Flask-WTF

from flask import Flask, request, render_template, flash, redirect, url_for, session
from wtforms import Form, StringField, TextAreaField, validators


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/status')
def status():
    return render_template('status.html')

@app.route('/configure', methods=['GET', 'POST'])
def configure():
    form = ConfigureForm(request.form)
    test1 = form.test1.data
    test2 = form.test2.data
    print (test1)
    print (test2)
    return render_template('configure.html', form=form, test1=test1, test2=test2)


@app.route('/about')
def about():
    return render_template('about.html')

class ConfigureForm(Form):
    test1 = StringField('test1')
    test2 = StringField('test2')

if __name__ == '__main__':
    app.run(debug=True)
