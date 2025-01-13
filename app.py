from flask import Flask, render_template, jsonify, send_from_directory
import os
import pickle

app = Flask(__name__)

# Directory containing PDB files and path to tokens pickle file
PDB_DIR = '/home/dom/Desktop/Coding/protein_website_2/pdb/'
TOKEN_FILE = '/home/dom/Desktop/Research/HalM2/D2O/D2O_7.0/tokens_data1.pkl'

def flatten_tokens(data):
    """
    Recursively extract all numeric values from a nested dictionary.
    This is used to compute global min/max token values across all frames.
    """
    numeric_values = []
    if isinstance(data, dict):
        for val in data.values():
            if isinstance(val, dict):
                numeric_values.extend(flatten_tokens(val))
            elif isinstance(val, (int, float)):
                numeric_values.append(val)
    return numeric_values

@app.route('/')
def index():
    """Render the main page with the viewer."""
    return render_template('index.html')

@app.route('/pdb_files')
def list_pdb_files():
    """Return a JSON list of available PDB files in the specified directory."""
    files = [f for f in os.listdir(PDB_DIR) if f.endswith('.pdb')]
    return jsonify(files)

@app.route('/pdb/<filename>')
def get_pdb_file(filename):
    """Serve a specific PDB file from the server."""
    return send_from_directory(PDB_DIR, filename)

@app.route('/tokens/<int:frame_num>')
def get_frame_tokens(frame_num):
    """
    Retrieve token data for a specified frame number, along with
    global min and max token values across all frames.
    """
    try:
        # Load token data from pickle file
        with open(TOKEN_FILE, 'rb') as f:
            token_data = pickle.load(f)

        # Get token data for the requested frame
        frame_data = token_data.get(frame_num, {})
        if not frame_data:
            return jsonify({'error': f'No data for frame {frame_num}'}), 404

        # Compute global min and max across all frames
        all_tokens = []
        for _, frame_dict in token_data.items():
            all_tokens.extend(flatten_tokens(frame_dict))

        if not all_tokens:
            return jsonify({'error': 'No numeric tokens found in data.'}), 500

        token_min = min(all_tokens)
        token_max = max(all_tokens)

        # Respond with the frame's token data and global min/max values
        return jsonify({
            'frameData': frame_data,
            'tokenMin': token_min,
            'tokenMax': token_max
        })

    except Exception as e:
        print(f"Error loading frame {frame_num}:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
