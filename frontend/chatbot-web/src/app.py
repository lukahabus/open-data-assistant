from flask import Flask, render_template, request
from chatbot import chatbot

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    response = ""
    if request.method == 'POST':
        street_name = request.form['street_name']
        response = chatbot(street_name)
    return render_template('index.html', response=response)

if __name__ == '__main__':
    app.run(debug=True)