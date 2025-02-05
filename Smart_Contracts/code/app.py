from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
import numpy as np
# from joblib import load
from fastapi.middleware.cors import CORSMiddleware

# Initialize the FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load data from CSV file
csv_file_path = 'smart_contract_dataset.csv'  # Replace with your actual file path
df = pd.read_csv(csv_file_path)

# Create label encoders for each feature
label_encoders = {}
for column in ['Code Snippet', 'Function Call Patterns', 'Control Flow Graph', 'Opcode Sequence']:
    label_encoders[column] = LabelEncoder()
    df[column] = label_encoders[column].fit_transform(df[column])

# Features and labels
X = df.drop(columns=['Label', 'Contract ID'])
y = df['Label']

# Load your pre-trained models (for demonstration, we're using new models here)
rf_model = RandomForestClassifier()
svm_model = SVC(probability=True)
gb_model = GradientBoostingClassifier()

# Load your pre-trained models
# rf_model = load("rf_model.joblib")
# svm_model = load("svm_model.joblib")
# gb_model = load("gb_model.joblib")

# Train the models (in practice, you'd load pre-trained models)
rf_model.fit(X, y)
svm_model.fit(X, y)
gb_model.fit(X, y)

# Define the input data model
class InputData(BaseModel):
    code_snippet: str
    function_call_patterns: str
    control_flow_graph: str
    opcode_sequence: str

# Endpoint for predictions
@app.post("/predict/")
def predict(input_data: InputData):
    try:
        # Encode the inputs using the fitted label encoders
        encoded_input = {
            'Code Snippet': label_encoders['Code Snippet'].transform([input_data.code_snippet])[0],
            'Function Call Patterns': label_encoders['Function Call Patterns'].transform([input_data.function_call_patterns])[0],
            'Control Flow Graph': label_encoders['Control Flow Graph'].transform([input_data.control_flow_graph])[0],
            'Opcode Sequence': label_encoders['Opcode Sequence'].transform([input_data.opcode_sequence])[0]
        }

        user_input_df = pd.DataFrame([encoded_input])

        # Make predictions
        rf_predictions = rf_model.predict(user_input_df)
        svm_predictions = svm_model.predict(user_input_df)
        gb_predictions = gb_model.predict(user_input_df)

        # Convert NumPy types to standard Python types
        return {
            "RandomForest": int(rf_predictions[0]),
            "SVM": int(svm_predictions[0]),
            "GradientBoosting": int(gb_predictions[0])
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
