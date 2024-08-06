# API Endpoints Testing Guide

This document provides instructions on how to test the API endpoints for the Flask application deployed on IBM Code Engine. The application handles document versioning and provides responses based on uploaded data.

## Application URL

The application is accessible at:

[https://application-flaskapi-ziraat.1egxtnzrl4dm.us-south.codeengine.appdomain.cloud/](https://application-flaskapi-ziraat.1egxtnzrl4dm.us-south.codeengine.appdomain.cloud/)

## Endpoints

### 1. **GET /**

- **Description**: Fetches the main index page of the application.
- **URL**: `https://application-flaskapi-ziraat.1egxtnzrl4dm.us-south.codeengine.appdomain.cloud/`
- **Method**: `GET`
- **Response**: Main page content or status message.

#### Example Request

1. Open Postman.
2. Set the request type to `GET`.
3. Enter the URL: `https://application-flaskapi-ziraat.1egxtnzrl4dm.us-south.codeengine.appdomain.cloud/`
4. Click "Send".

### 2. **POST /upload_pdfs**

- **Description**: Upload PDF files to create or update the document vector store.
- **URL**: `https://application-flaskapi-ziraat.1egxtnzrl4dm.us-south.codeengine.appdomain.cloud/upload_pdfs`
- **Method**: `POST`
- **Body**: Form-data
  - Key: `pdf_files` (Type: File)
  - Upload one or more PDF files.
- **Response**: Confirmation message on successful upload and processing.

#### Example Request

1. Open Postman.
2. Set the request type to `POST`.
3. Enter the URL: `https://application-flaskapi-ziraat.1egxtnzrl4dm.us-south.codeengine.appdomain.cloud/upload_pdfs`
4. Go to the "Body" tab and select "form-data".
5. Add a key named `pdf_files` and set the type to "File". Upload the desired PDF file(s).
6. Click "Send".

### 3. **POST /upload_excel**

- **Description**: Upload an Excel file containing questions and receive answers.
- **URL**: `https://application-flaskapi-ziraat.1egxtnzrl4dm.us-south.codeengine.appdomain.cloud/upload_excel`
- **Method**: `POST`
- **Body**: Form-data
  - Key: `excel_file` (Type: File)
  - Upload an Excel file with a column named `Soru` for questions.
- **Response**: Confirmation message with a URL to download the processed Excel file.

#### Example Request

1. Open Postman.
2. Set the request type to `POST`.
3. Enter the URL: `https://application-flaskapi-ziraat.1egxtnzrl4dm.us-south.codeengine.appdomain.cloud/upload_excel`
4. Go to the "Body" tab and select "form-data".
5. Add a key named `excel_file` and set the type to "File". Upload the desired Excel file.
6. Click "Send".

### 4. **GET /download_processed_excel**

- **Description**: Download the processed Excel file with answers.
- **URL**: `https://application-flaskapi-ziraat.1egxtnzrl4dm.us-south.codeengine.appdomain.cloud/download_processed_excel`
- **Method**: `GET`
- **Response**: The processed Excel file as an attachment, or an error message if the file is not found.

#### Example Request

1. Open Postman.
2. Set the request type to `GET`.
3. Enter the URL: `https://application-flaskapi-ziraat.1egxtnzrl4dm.us-south.codeengine.appdomain.cloud/download_processed_excel`
4. Click "Send".

### 5. **POST /ask_question**

- **Description**: Submit a question to get a response based on the processed documents.
- **URL**: `https://application-flaskapi-ziraat.1egxtnzrl4dm.us-south.codeengine.appdomain.cloud/ask_question`
- **Method**: `POST`
- **Body**: JSON
  - Key: `query` (Value: The question you want to ask)
  ```json
  {
    "query": "Your question here"
  }
  ```
- **Response**: JSON containing the response to the question.

#### Example Request

1. Open Postman.
2. Set the request type to `POST`.
3. Enter the URL: `https://application-flaskapi-ziraat.1egxtnzrl4dm.us-south.codeengine.appdomain.cloud/ask_question`
4. Go to the "Body" tab and select "raw". Choose "JSON" from the dropdown menu.
5. Enter the JSON payload:
   ```json
   {
     "query": "Your question here"
   }
   ```
6. Click "Send".

## Notes

- Ensure that the application is up and running before testing the endpoints.
- Review the responses to verify correct functionality.
- For any issues or feedback, please contact [Your Contact Information].
