from flask import Flask, render_template, request, jsonify
import requests
import random
from tractor_facts import tractor_facts

app = Flask(__name__)

def get_random_image():
    # Unsplash API URL to fetch a random image with "tractor" keyword
    url = "https://source.unsplash.com/random/?tractor"
    
    # Make a request to the Unsplash API
    response = requests.get(url)
    
    if response.status_code == 200:
        # Get the image URL from the response
        image_url = response.url
        return image_url
    else:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        image_url = get_random_image()
        tractor_fact = random.choice(tractor_facts)
        return render_template("index.html", image_url=image_url, tractor_fact=tractor_fact)
    else:
        return render_template("index.html", image_url=None, tractor_fact=None)

@app.route("/random-tractor-fact", methods=["GET"])
def random_tractor_fact():
    fact = random.choice(tractor_facts)
    return jsonify({"fact": fact})

if __name__ == "__main__":
    app.run(debug=True)
