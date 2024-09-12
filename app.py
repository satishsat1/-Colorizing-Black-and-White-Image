from flask import Flask, render_template, request
import numpy as np
import cv2
import os
import argparse
import pickle
import io

app = Flask(__name__)

prototxt = "model/colorization_deploy_v2.prototxt"
points = "model/pts_in_hull.npy"
model = "model/colorization_release_v2.caffemodel"

net = cv2.dnn.readNetFromCaffe(prototxt, model)
pts = np.load(points)

class8 = net.getLayerId("class8_ab")
conv8 = net.getLayerId("conv8_313_rh")
pts = pts.transpose().reshape(2, 313, 1, 1)
net.getLayer(class8).blobs = [pts.astype("float32")]
net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]

def colorize_image(image):
    scaled = image.astype("float32") / 255
    lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)

    resized = cv2.resize(lab, (224, 224))
    l = cv2.split(resized)[0]
    l -= 50  # hyper parameter

    net.setInput(cv2.dnn.blobFromImage(l))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))
    ab = cv2.resize(ab, (image.shape[1], image.shape[0]))

    l = cv2.split(lab)[0]
    colorized = np.concatenate((l[:, :, np.newaxis], ab), axis=2)

    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
    colorized = np.clip(colorized, 0, 1)
    colorized = (255 * colorized).astype("uint8")
    return colorized

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return 'No file uploaded'

    image_file = request.files['image']
    image_data = image_file.read()
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return 'Error: Unable to load image'

    colorized_image = colorize_image(image)

    img_bytes = cv2.imencode('.jpg', colorized_image)[1].tobytes()

    return f'<img src="data:image/jpeg;base64,{img_bytes.decode("utf-8")}" alt="Colorized Image">'

if __name__ == '__main__':
    app.run(debug=True)
