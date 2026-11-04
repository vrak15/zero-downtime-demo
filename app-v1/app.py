from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Version 1 - Stable</h1>"

@app.route('/health')
def health():
    return {"status": "healthy", "version": "v1"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
