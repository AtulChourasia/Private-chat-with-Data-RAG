from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/init', methods=['POST'])
def init_model():
    try:
        from worker import init_llm
        init_llm()
        return jsonify({"status": "success", "message": "Model initialized successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
