from flask import Flask, render_template
app = Flask(__name__, static_url_path="/static", static_folder='static')


@app.route("/")
def hello():
    z = "<h1 style='color:blue'>Hello There!</h1>"
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
