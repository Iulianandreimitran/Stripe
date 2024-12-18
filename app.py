from flask import Flask, request, jsonify
from flask_cors import CORS
from analysis import run_analysis_with_token

app = Flask(__name__)
CORS(app)

@app.route('/store-token', methods=['POST'])
def store_token():
    data = request.get_json()
    access_token = data.get('access_token')

    if not access_token:
        return jsonify({"error": "No token provided"}), 400

    predicted_mbti, recommended_jobs = run_analysis_with_token(access_token)
    if not predicted_mbti:
        return jsonify({"error": "No MBTI could be predicted"}), 500

    return jsonify({
        "status": "success",
        "predicted_mbti": predicted_mbti,
        "recommended_jobs": recommended_jobs
    })

if __name__ == '__main__':
    app.run(port=5000)
