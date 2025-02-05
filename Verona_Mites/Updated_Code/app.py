from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image
from PIL import Image
import numpy as np
import uvicorn

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify the origins allowed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load the model
model = load_model('model.h5')

# Class names (replace with your actual class names)
class_names = ['healthy', 'varroa', 'ants', 'few_var', 'robbed']

# @app.post("/predict/")
# async def predict_image(file: UploadFile = File(...)):
#     try:
#         img = Image.open(file.file).convert("RGB")
#         img = img.resize((180, 180))  # Adjust based on your model input size
#         img_array = keras_image.img_to_array(img)
#         img_array = np.expand_dims(img_array, axis=0)

#         predictions = model.predict(img_array)
#         score = tf.nn.softmax(predictions[0])
#         predicted_class = class_names[np.argmax(score)]

#         return JSONResponse(content={
#             "predicted_class": predicted_class,
#             "confidence": f"{100 * np.max(score):.2f}%"
#         })
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error processing image: {e}")
import logging

logging.basicConfig(level=logging.DEBUG)

@app.post("/predict/")
async def predict_image(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    try:
        logging.debug("Received file: %s", file.filename)
        img = Image.open(file.file).convert("RGB")
        img = img.resize((180, 180))  # Adjust based on your model input size
        img_array = keras_image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        
        logging.debug("Image array shape: %s", img_array.shape)

        predictions = model.predict(img_array)
        logging.debug("Predictions: %s", predictions)

        if len(predictions) == 0:
            raise HTTPException(status_code=500, detail="Empty predictions received")

        score = tf.nn.softmax(predictions[0])
        logging.debug("Score: %s", score)

        if not class_names or len(class_names) == 0:
            raise HTTPException(status_code=500, detail="Class names not defined")

        predicted_class = class_names[np.argmax(score)]
        logging.debug("Predicted class: %s", predicted_class)

        if predicted_class in ['varroa', 'few_var', 'healthy']:
            # confidence = 100 * np.max(score)
        # else:
            # predicted_class = 'prediction out of the classification'
            # confidence = 0

            return JSONResponse(content={
                "predicted_class": predicted_class,
                "confidence": f"{100 * np.max(score):.2f}%"
            })
        else:
            return JSONResponse(content={
                "predicted_class": 'prediction out of the classification',
                "confidence": 0
            })

    except Exception as e:
        logging.error("Error processing image: %s", str(e))
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")



# @app.get("/model-summary/")
# async def get_model_summary():
#     stringlist = []
#     model.summary(print_fn=lambda x: stringlist.append(x))
#     summary = "\n".join(stringlist)
#     return JSONResponse(content={"model_summary": summary})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)



# from fastapi import FastAPI, UploadFile, File
# from fastapi.responses import JSONResponse
# from PIL import Image
# import numpy as np
# import tensorflow as tf
# from tensorflow.keras.models import load_model
# import io

# app = FastAPI()

# # Load the model
# model = load_model('model.h5')
# img_height, img_width = 180, 180
# class_names = ['healthy', 'varroa', 'ants', 'few_var', 'robbed']  # Replace with your actual class names

# # Preprocess the image
# def preprocess_image(image: Image.Image) -> np.ndarray:
#     image = image.resize((img_width, img_height))
#     img_array = tf.keras.preprocessing.image.img_to_array(image)
#     img_array = tf.expand_dims(img_array, 0)  # Create a batch
#     img_array = img_array / 255.0  # Normalize
#     return img_array

# @app.post("/predict/")
# async def predict(file: UploadFile = File(...)):
#     image = Image.open(io.BytesIO(await file.read()))
#     img_array = preprocess_image(image)
    
#     predictions = model.predict(img_array)
#     score = tf.nn.softmax(predictions[0])
    
#     predicted_class = class_names[np.argmax(score)]

#     if predicted_class in ['varroa', 'few_var', 'healthy']:
#         confidence = 100 * np.max(score)
#     else:
#         predicted_class = 'prediction out of the classification'
#         confidence = 0
    
#     return JSONResponse(content={
#         "class": predicted_class,
#         "confidence": confidence
#     })

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
