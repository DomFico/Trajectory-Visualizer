# Protein Trajectory Visualization and Tokenization

https://github.com/user-attachments/assets/ae7bb3d4-924e-4686-9631-5d1f081f4dfc

## Overview
This project provides a framework to visualize protein trajectory structures and annotate each residue with a scalar value. It uses the Evolutionary Scale Modeling (ESM) tokenizer to process protein structures frame by frame and paints the trajectory structures with token values for enhanced visualization and analysis.

The project is composed of multiple components:
- **Web Application**: A Flask-based web app to display protein trajectories interactively.
- **Data Conversion**: Scripts to convert molecular dynamics simulation outputs to formats compatible with the web application.
- **ESM Tokenization**: Scripts to tokenize residue-level features for each frame in the trajectory using ESM models.

## Features
1. **Interactive Viewer**:
   - Visualize protein structures using 3Dmol.js in a draggable and resizable viewer.
   - Navigate through trajectory frames interactively.

2. **Residue Tokenization**:
   - Tokenize each residue using the ESM tokenizer.
   - Annotate residue structures with scalar values for visualization.

3. **Trajectory Conversion**:
   - Convert `.parm7` and `.nc` files from molecular dynamics simulations to `.pdb` format.
   - Skip specified frames to optimize processing.

4. **Global Min/Max Token Analysis**:
   - Compute and display global minimum and maximum token values across all frames.

## File Descriptions

### Python Scripts

- **`app.py`**:
  - Main Flask application that serves the web interface.
  - Provides routes to list PDB files, retrieve tokens for frames, and visualize structures interactively.

- **`converter.py`**:
  - Converts `.parm7` and `.nc` trajectory files to `.pdb` format.
  - Processes specified frames from molecular dynamics simulations for visualization and analysis.

- **`tokenizer.py`**:
  - Handles ESM tokenization for each residue in the trajectory frames.
  - Renames non-standard residues for compatibility with the ESM model.
  - Saves token data in a pickle file for later use.

### HTML and JavaScript

- **`index.html`**:
  - Frontend interface for visualizing protein trajectories.
  - Includes controls for navigating through trajectory frames and viewing residue information.

- **`main.js`**:
  - Implements frame navigation and interaction with the backend API.
  - Provides drag-and-resize functionality for windows.

## Installation

### Prerequisites
- Python 3.8+
- Flask
- MDTraj
- BioPython
- Evolutionary Scale Modeling (ESM) SDK
- 3Dmol.js (integrated in `index.html`)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/DomFico/Trajectory-Visualizer.git
   cd <repository_directory>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up file paths in `app.py`, `converter.py`, and `tokenizer.py` to point to your local directories for PDB files, trajectories, and token data.
4. Start the Flask application:
   ```bash
   python app.py
   ```
5. Open your browser and navigate to `http://127.0.0.1:5000/` to access the application.

## Usage

### Tokenization Workflow
1. Convert your `.parm7` and `.nc` files to `.pdb` format using `converter.py`:
   ```bash
   python converter.py
   ```
   Ensure that the token data file path is correctly set.

2. Run the `tokenizer.py` script to tokenize the frames and generate the token pickle file:
   ```bash
   python tokenizer.py
   ```

3. Launch the Flask app and interact with the visualized structures and residue tokens.

### Web Application
- **Load PDB**: Click "Load PDB" to select a structure.
- **Frame Navigation**: Use the "Previous," "Next," "Play," and "Stop" buttons to navigate through trajectory frames.
- **Residue Info**: View tokenized residue details in the draggable information panel.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any feature suggestions or bug fixes.

