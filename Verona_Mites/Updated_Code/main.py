from flask import Flask, request, jsonify
import tensorflow as tf
from tensorflow.keras.preprocessing import image as keras_image
import numpy as np
import os

app = Flask(__name__)

# Load the model
model = tf.keras.models.load_model('model.h5')
class_names = ['healthy', 'varroa', 'unhealthy', 'few_var', 'robbed', 'ants']  # Replace with your actual class names

# Image size expected by the model
img_height, img_width = 180, 180

def prepare_image(img_path):
    """Load and preprocess the image."""
    img = keras_image.load_img(img_path, target_size=(img_height, img_width))
    img_array = keras_image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch
    return img_array

@app.route('/predict', methods=['POST'])
def predict():
    """Predict the class of the image."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Save the file
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        
        # Prepare and predict
        img_array = prepare_image(file_path)
        predictions = model.predict(img_array)
        score = tf.nn.softmax(predictions[0])
        
        # Get the prediction result
        predicted_class = class_names[np.argmax(score)]
        confidence = 100 * np.max(score)
        
        return jsonify({
            'class': predicted_class,
            'confidence': confidence
        })
    
    return jsonify({'error': 'File not found'}), 400

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    app.run(debug=True)
