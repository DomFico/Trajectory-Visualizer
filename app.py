from flask import Flask, render_template, jsonify, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/xyz_files')
def get_xyz_files():
    xyz_dir = os.path.join(os.getcwd(), 'xyz')
    xyz_files = [f for f in os.listdir(xyz_dir) if f.endswith('.xyz')]
    return jsonify(xyz_files)

@app.route('/xyz/<filename>')
def serve_xyz_file(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'xyz'), filename)

if __name__ == '__main__':
    app.run(debug=True)
