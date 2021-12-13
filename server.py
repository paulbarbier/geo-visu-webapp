#!/usr/bin/python3

import os
from flask import Flask
from flask import render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
UPLOAD_FOLDER = "uploads"

#dummy function for testing purposes
def compute_match(image_filename):
    return {"x" : 1, "y" : 1}

app = Flask(__name__)
app.secret_key = "kvhkjbi187897JNBBbhb!:" #needed for flash messages
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods = ["GET", "POST"])
def index(image_filename = None, position_match = None):
    if request.method == "POST":
        if "image" not in request.files:
            flash("No image provided in the request.")
            return redirect(request.url)
        image = request.files["image"]
        if image.filename == "":
            flash("Empty image provided.")
            return redirect(request.url)
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            position_match = compute_match(image_filename)

            return render_template("index.html", image_filename = filename, position_match = position_match)
        else:
            flash("Wring image format. Please provide an image with PNG, JPEG or JPG format.")
    return render_template("index.html", image_filename = image_filename, position_match = position_match)

@app.route("/uploads/<filename>")
def render_image(filename):
    #return redirect(url_for("static", filename = "uploads/" + filename))
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/database")
def database():
    return render_template("database.html")

@app.route("/geolocalizer")
def geolocalizer():
    return render_template("geolocalizer.html")

@app.route("/about")
deg about():
    return render_template("about.html")

if __name__ == "__main__":
    app.debug = True
    app.run()
