from flask import Flask, request, jsonify, render_template
from Ziraat_Bank_Assistant_App import ZiraatBankQA
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the QA system with logger
qa_system = ZiraatBankQA(config_path='config.ini', logger=logger)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask_question', methods=['POST'])
def ask_question():
    data = request.json
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    try:
        response, _ = qa_system.main(query)
        return jsonify({'response': response}), 200
    except ValueError as e:
        logger.error(f"ValueError: {e}")
        return jsonify({'error': 'Collection does not exist or could not be loaded.'}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Collection does not exist or could not be loaded.'}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8510)
