import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from flask import Flask, request, render_template

app = Flask(__name__)

# Load the trained model
model = tf.keras.models.load_model('best_model.keras')

# Image preprocessing function
def preprocess_image(image_path):
    img = load_img(image_path, target_size=(128, 128))
    img_array = img_to_array(img) / 255.0  # Ensure consistent preprocessing
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)

            # Process the image
            img_array = preprocess_image(file_path)

            # Predict
            prediction = model.predict(img_array)[0][0]

            # Remove the uploaded file
            os.remove(file_path)

            # Adjust the threshold if needed
            threshold = 0.5
            result = 'Yes' if prediction > threshold else 'No'

            return f"Varroa mite detected: {result} (Confidence: {prediction:.2f})"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
