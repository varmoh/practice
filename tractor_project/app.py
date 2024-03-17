from flask import Flask, render_template, request, jsonify, make_response
import requests
import random
import json

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

def load_translations(language):
    with open(f"translations_{language}.json", "r", encoding="utf-8") as file:
        translations = json.load(file)
    return translations

languages = ["en", "lt", "et"]

@app.route("/", methods=["GET", "POST"])
def index():
    language = request.cookies.get("language", "en")
    if language not in languages:
        language = "en"
    
    translations = load_translations(language)

    if request.method == "POST":
        image_url = get_random_image()
        tractor_fact = random.choice(translations["facts"])
        return render_template("index.html", image_url=image_url, tractor_fact=tractor_fact, translations=translations)
    else:
        return render_template("index.html", image_url=None, tractor_fact=None, translations=translations)

@app.route("/random-tractor-fact", methods=["GET"])
def random_tractor_fact():
    language = request.cookies.get("language", "en")
    if language not in languages:
        language = "en"
    
    translations = load_translations(language)
    
    fact = random.choice(translations["facts"])
    return jsonify({"fact": fact})

@app.route("/set-language/<language>", methods=["GET"])
def set_language(language):
    if language in languages:
        response = make_response()
        response.set_cookie("language", language)
        return response
    else:
        return jsonify({"error": "Invalid language"})

if __name__ == "__main__":
    app.run(debug=True)
