
###  Step 1: Start Your FastAPI Application

  

Make sure your FastAPI application is running. If you saved your script as `app.py`, start it using:

  

```bash

uvicorn  app:app  --reload

```

  

This will start the FastAPI server on `http://127.0.0.1:8000` by default.

  

###  Step 2: Open Postman

  

1. Open the Postman application on your computer.

2. Create a new request by clicking the "New" button or selecting "New Request" from the main menu.

  

###  Step 3: Set Up the POST Request

  

1.  **Set the Request Type to POST**:

- In the request dropdown (on the left side of the URL bar), select `POST`.

  

2.  **Enter the Request URL**:

- In the URL field, type `http://127.0.0.1:8000/predict/`.

  

3.  **Set the Request Body**:

- Click on the "Body" tab below the URL bar.

- Select the "raw" option.

- Choose "JSON" from the dropdown on the right side (it should be next to the "Text" option).

4.  **Enter the JSON Data**:

- In the text area, enter a JSON object that matches the `InputData` model. Here’s an example:

  

```json

{

"code_snippet":  "contract_kxcvnkkdehikzffrstdd",

"function_call_patterns":  "{call22, call91}",

"control_flow_graph":  "graph_hwustzmbve",

"opcode_sequence":  "opcodes_crjjzspsaggqsoh"

}

```

  

###  Step 4: Send the Request

  

1.  **Click "Send"**:

- After entering the data, click the "Send" button to submit the request to your FastAPI server.

  

###  Step 5: Review the Response

  

1.  **Check the Response**:

- After sending the request, Postman will display the response returned by the FastAPI server.

- You should see a JSON response with the predictions from the models:

  

```json

{

"RandomForest":  0,

"SVM":  1,

"GradientBoosting":  0

}

```

  

The values (`0`, `1`, etc.) will depend on your model predictions based on the input provided.

  

###  Troubleshooting

  

-  **Server Not Running**: Ensure your FastAPI server is running before sending the request.

-  **CORS Errors**: If you're accessing the server from a different domain or via localhost, CORS (Cross-Origin Resource Sharing) issues might occur. This shouldn't be a problem with Postman, but if it is, you can configure CORS in FastAPI.

-  **Invalid JSON**: Ensure that the JSON data in the request body is correctly formatted.

  

By following these steps, you should be able to successfully test your FastAPI API using Postman.

  
  

---
---

  
  
  

###  Testing With Frontend

Make sure your FastAPI application is running. If you saved your script as `app.py`, start it using:


```bash

uvicorn  app:app  --reload

```
  

This will start the FastAPI server on `http://127.0.0.1:8000` by default.


> Open the `Web App` using live server or directily using the html file, enter the respective data as shown:

  

**Enter the Data**:

- In the text area, enter a object that matches the `InputData` model. Here’s an example:

  

```json

{

"code_snippet":  "contract_kxcvnkkdehikzffrstdd",

"function_call_patterns":  "{call22, call91}",

"control_flow_graph":  "graph_hwustzmbve",

"opcode_sequence":  "opcodes_crjjzspsaggqsoh"

}

```

> Click on get prediction and get the responce, if the model is unable to predict the result it will throw thw result.