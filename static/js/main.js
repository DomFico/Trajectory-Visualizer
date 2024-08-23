// main.js

let element = document.querySelector('#container-01');
let config = { backgroundColor: 'white' };
let viewer = $3Dmol.createViewer(element, config);

let currentFrame = 0;
let trajectory = [];  // Array to hold multiple XYZ frames

// Function to load and render a specific frame
function renderFrame(frameIndex) {
    if (frameIndex < 0 || frameIndex >= trajectory.length) return;

    viewer.clear();
    const model = viewer.addModel();
    model.addAtoms(trajectory[frameIndex]);
    viewer.setStyle({}, { sphere: { radius: 0.3, color: 'spectrum' } });
    viewer.zoomTo();
    viewer.render();
}

// Fetch the available XYZ files from the server
function loadXYZFiles() {
    fetch('/xyz_files')  // Endpoint to get the list of XYZ files
        .then(response => response.json())
        .then(files => {
            trajectory = [];  // Clear previous trajectory data
            currentFrame = 0;

            // Fetch each XYZ file and parse it
            files.forEach((file, index) => {
                fetch(`/xyz/${file}`)
                    .then(response => response.text())
                    .then(data => {
                        const lines = data.split(/\r?\n/);
                        const atomCount = parseInt(lines[0].trim());

                        const atoms = [];
                        for (let i = 2; i < atomCount + 2; i++) {
                            const [elem, x, y, z] = lines[i].trim().split(/\s+/);
                            atoms.push({
                                elem: elem,
                                x: parseFloat(x),
                                y: parseFloat(y),
                                z: parseFloat(z)
                            });
                        }

                        trajectory.push(atoms);

                        // Automatically render the first frame after all files are loaded
                        if (index === files.length - 1) {
                            renderFrame(0);
                        }
                    });
            });
        })
        .catch(error => console.error('Error loading XYZ files:', error));
}

// Frame control
function nextFrame() {
    currentFrame = (currentFrame + 1) % trajectory.length;
    renderFrame(currentFrame);
}

function prevFrame() {
    currentFrame = (currentFrame - 1 + trajectory.length) % trajectory.length;
    renderFrame(currentFrame);
}

// Event listener for loading XYZ files
document.getElementById('loadXYZ').addEventListener('click', loadXYZFiles);
