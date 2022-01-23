#!/usr/bin/python3

import os
from flask import Flask
from flask import render_template, flash, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from skyline_computation import compute_skyline

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
UPLOAD_FOLDER = "uploads"

#function which computes the coordinates of the uploaded image
def compute_geolocalization(image_filename):
    skyline_filename = compute_skyline(image_filename)
    return 46.128, 6.399, skyline_filename

app = Flask(__name__)
app.secret_key = "kvhkjbi187897JNBBbhb!:" #needed for flash messages
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/geolocalizer")
def geolocalizer():
    return render_template("geolocalizer.html")

@app.route("/upload_image/", methods = ["POST"])
def upload_image():
    lat = 0
    lon = 0
    skyline_filename = ""
    
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

        lat, lon, skyline_filename = compute_geolocalization(filename)
    else:
        flash("Error! Please provide an image with PNG, JPEG or JPG format.")

    return jsonify({"lat" : lat, "lon" : lon, "skyline_filename" : skyline_filename})

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
