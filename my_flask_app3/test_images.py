from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/test')
def test():
    return """
    <html>
    <head><title>Image Test</title></head>
    <body>
        <h1>Image Test</h1>
        <div>
            <h2>Direct static image (should work)</h2>
            <img src="/static/images/maggi.jpg" alt="Maggi">
        </div>
        <div>
            <h2>Static without leading slash (should work)</h2>
            <img src="static/images/maggi.jpg" alt="Maggi">
        </div>
        <div>
            <h2>Images folder only (should fail without our fix)</h2>
            <img src="/images/maggi.jpg" alt="Maggi">
        </div>
        <div>
            <h2>Images folder only without slash (should fail without our fix)</h2>
            <img src="images/maggi.jpg" alt="Maggi">
        </div>
        <div>
            <h2>Direct filename (should fail without our fix)</h2>
            <img src="maggi.jpg" alt="Maggi">
        </div>
    </body>
    </html>
    """

@app.route('/images/<path:filename>')
def serve_image(filename):
    # Allow access to images directly
    return send_from_directory('static/images', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5001) 