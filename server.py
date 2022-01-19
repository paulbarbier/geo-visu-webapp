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

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/geolocalizer", methods = ["GET", "POST"])
def geolocalizer(image_filename = None, position_match = None):
    if request.method == "POST":
        if "image" not in request.files:
            flash("Error! Please provide an image.")
            return redirect(request.url)
        image = request.files["image"]
        if image.filename == "":
            flash("Error! Please provide a non-empty image.")
            return redirect(request.url)
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            position_match = compute_match(image_filename)

            return render_template("geolocalizer.html", image_filename = filename, position_match = position_match)
        else:
            flash("Error! Please provide an image with PNG, JPEG or JPG format.")
    return render_template("geolocalizer.html", image_filename = image_filename, position_match = position_match)

@app.route("/uploads/<filename>")
def render_image(filename):
    #return redirect(url_for("static", filename = "uploads/" + filename))
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/database")
def database():
    return render_template("database.html")
def show_index():
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'test2.jpg')
    return render_template("database.html", user_image = full_filename)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.debug = True
    app.run()
