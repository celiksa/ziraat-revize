from flask import Flask, request, jsonify, send_file, render_template
import os
import pandas as pd
from io import BytesIO
from Ziraat_Bank_Assistant_App import ZiraatBankQA

app = Flask(__name__)

# Directory for uploaded PDFs and Excel files
UPLOAD_FOLDER = 'uploaded_pdfs'
EXCEL_FOLDER = 'uploaded_excel'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXCEL_FOLDER, exist_ok=True)

qa_system = ZiraatBankQA(config_path='config.ini')  # Initialize the QA system

def check_pdf_size(pdf_files):
    total_size = sum([file.content_length for file in pdf_files])
    return total_size <= 200 * 1024 * 1024  # Changed to 200 MB

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_pdfs', methods=['POST'])
def upload_pdfs():
    if 'pdf_files' not in request.files:
        return jsonify({'error': 'No PDF files uploaded'}), 400

    pdf_files = request.files.getlist('pdf_files')
    if not pdf_files:
        return jsonify({'error': 'No files selected'}), 400

    if not check_pdf_size(pdf_files):
        return jsonify({'error': 'Total PDF size exceeds 200 MB'}), 400

    for pdf_file in pdf_files:
        file_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
        pdf_file.save(file_path)

    text_chunks = qa_system.load_documents(UPLOAD_FOLDER)
    vector_db = qa_system.create_vector_store(text_chunks)

    return jsonify({'message': 'PDFs uploaded and vector store created successfully'}), 200

@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    if 'excel_file' not in request.files:
        return jsonify({'error': 'No Excel file uploaded'}), 400

    excel_file = request.files['excel_file']
    excel_path = os.path.join(EXCEL_FOLDER, 'questions.xlsx')
    excel_file.save(excel_path)

    # Process Excel file
    df = pd.read_excel(excel_path, engine='openpyxl')
    questions = df['Soru'].tolist()
    responses = [qa_system.main(question, folder_path=UPLOAD_FOLDER)[0] for question in questions]
    df['response'] = responses
    
    output_excel = BytesIO()
    df.to_excel(output_excel, index=False, engine='openpyxl')
    output_excel.seek(0)

    # Save the processed file
    processed_file_path = os.path.join(EXCEL_FOLDER, 'Ziraat_QnA_LLM_Responses.xlsx')
    with open(processed_file_path, 'wb') as f:
        f.write(output_excel.read())
    
    return jsonify({'message': 'Excel file processed successfully', 'file_url': '/download_processed_excel'}), 200

@app.route('/download_processed_excel', methods=['GET'])
def download_processed_excel():
    processed_file_path = os.path.join(EXCEL_FOLDER, 'Ziraat_QnA_LLM_Responses.xlsx')
    if os.path.exists(processed_file_path):
        return send_file(processed_file_path, as_attachment=True, download_name='Ziraat_QnA_LLM_Responses.xlsx')
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/ask_question', methods=['POST'])
def ask_question():
    data = request.json
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    response, _ = qa_system.main(query, folder_path=UPLOAD_FOLDER)
    
    return jsonify({'response': response}), 200

if __name__ == "__main__":
    app.run(debug=True , port = 8510)
