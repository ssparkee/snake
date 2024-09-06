from flask import Flask, request, jsonify
from uuid import uuid4

app = Flask(__name__)


@app.route('/message', methods=['POST'])
def receive_message():
    data = request.json
    print(f"Received: {data}")
    return jsonify({'response': 'Message received!'})

@app.route('/connect', methods=['POST'])
def initConnect():
    data = request.json
    return jsonify({''})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
