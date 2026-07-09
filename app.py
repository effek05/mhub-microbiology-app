from flask import Flask
from flask import request
from flask import render_template
from main import big

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/impressum")
def imp():
    return render_template('impressum.html')

@app.route("/species")
def spec():
    return render_template('species.html')

@app.route("/progress")
def progr():
    return render_template('progress.html')

@app.route("/profile")
def prof():
    return render_template('profile.html')

@app.route("/focus")
def fock():
    return render_template('focus.html')

@app.route('/background_process_test')
def background_process_test():
    if request.method == 'GET':
        tim = request.args.get('ty')
        big(tim)
    return "nothing"

if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000, debug=True)
