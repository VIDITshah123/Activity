from flask import Flask, render_template, request
import requests

app = Flask(__name__)
API_URL = "http://127.0.0.1:8000/api/search"

@app.route("/", methods=["GET","POST"])
def index():
    products = []
    source = None
    if request.method == "POST":
        keyword = request.form["keyword"]
        r = requests.post(API_URL, params={"keyword": keyword})
        data = r.json()
        products = data["products"]
        source = data["source"]
    return render_template("index.html", products=products, source=source)
app.run(debug=True)