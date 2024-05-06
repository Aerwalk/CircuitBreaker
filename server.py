from flask import Flask, jsonify
import random
import time

app = Flask(__name__)

@app.route('/api')
def api():
    if random.random() < 0.5:  # Имитация периодической ошибки
        return jsonify({"error": "Server error"}), 500
    else:
        return jsonify({"message": "Success"})

if __name__ == '__main__':
    app.run(debug=True)