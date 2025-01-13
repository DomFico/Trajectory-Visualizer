let element = document.querySelector('#container-01');
let viewer = $3Dmol.createViewer(element, { backgroundColor: 'white' });

let currentFrame = 0;
let trajectory = [];
let isPlaying = false;
let playInterval;

/**
 * Maps a token value to an RGB color on a blue-to-red gradient.
 */
function getColorFromToken(token, min, max) {
    if (max === min) return 'rgb(0,0,255)'; // Default to blue
    const normalized = (token - min) / (max - min);
    const blue = Math.floor(255 * (1 - normalized));
    const red = Math.floor(255 * normalized);
    return `rgb(${red},0,${blue})`;
}

/**
 * Populates the residue info window.
 */
function populateResidueInfo(frameData, minToken, maxToken) {
    const residueInfoElement = document.getElementById('residueContent');
    residueInfoElement.innerHTML = '';
    Object.entries(frameData).forEach(([residueId, data]) => {
        const tokenVal = Array.isArray(data.token)
            ? data.token.reduce((sum, val) => sum + val, 0) / data.token.length
            : data.token;
        const color = getColorFromToken(tokenVal, minToken, maxToken);
        const residueDiv = document.createElement('div');
        residueDiv.innerHTML = `
            <span><strong>Residue:</strong> ${residueId}</span>
            <span><strong>Token:</strong> ${tokenVal.toFixed(2)}</span>
            <span><strong>Color:</strong> 
              <span style="display:inline-block; width:20px; height:20px; background-color:${color};"></span>
            </span>
        `;
        residueInfoElement.appendChild(residueDiv);
    });
}

/**
 * Renders a PDB frame and updates residue info.
 */
async function renderPDBFrame(frameIndex) {
    const pdbFilename = trajectory[frameIndex];
    const actualFrameNum = parseInt(pdbFilename.match(/\d+/)[0]);

    try {
        const [tokenResponse, pdbResponse] = await Promise.all([
            fetch(`/tokens/${actualFrameNum}`),
            fetch(`/pdb/${pdbFilename}`),
        ]);

        const tokenData = await tokenResponse.json();
        const pdbData = await pdbResponse.text();

        if (tokenData.error) {
            console.error(`Token data error: ${tokenData.error}`);
            return;
        }

        viewer.clear();
        viewer.addModel(pdbData, "pdb");

        const residueColors = {};
        Object.entries(tokenData.frameData).forEach(([residueId, data]) => {
            const tokenVal = Array.isArray(data.token)
                ? data.token.reduce((sum, val) => sum + val, 0) / data.token.length
                : data.token;
            residueColors[residueId] = getColorFromToken(tokenVal, tokenData.tokenMin, tokenData.tokenMax);
        });

        const colorScheme = (atom) => residueColors[atom.resi.toString()] || 'gray';
        viewer.setStyle({}, { cartoon: { colorfunc: colorScheme } });
        viewer.zoomTo();
        viewer.render();

        document.getElementById('frameCounter').textContent = `Frame: ${frameIndex + 1} (Actual: ${actualFrameNum})`;

        populateResidueInfo(tokenData.frameData, tokenData.tokenMin, tokenData.tokenMax);
    } catch (error) {
        console.error(`Error rendering frameIndex=${frameIndex}:`, error);
    }
}

/**
 * Loads available PDB files and renders the first frame.
 */
async function loadPDBFiles() {
    try {
        const response = await fetch('/pdb_files');
        trajectory = (await response.json()).sort((a, b) => {
            const numA = parseInt(a.match(/\d+/)[0]);
            const numB = parseInt(b.match(/\d+/)[0]);
            return numA - numB;
        });
        currentFrame = 0;
        await renderPDBFrame(currentFrame);
    } catch (error) {
        console.error('Error loading PDB files:', error);
    }
}

function nextFrame() {
    if (currentFrame < trajectory.length - 1) {
        currentFrame++;
        renderPDBFrame(currentFrame);
    } else {
        stopFrames();
    }
}

function prevFrame() {
    if (currentFrame > 0) {
        currentFrame--;
        renderPDBFrame(currentFrame);
    }
}

function playFrames() {
    if (isPlaying) return;
    isPlaying = true;
    playInterval = setInterval(() => {
        if (currentFrame < trajectory.length - 1) {
            nextFrame();
        } else {
            stopFrames();
        }
    }, 100);
}

function stopFrames() {
    isPlaying = false;
    clearInterval(playInterval);
}

// Event listeners
document.getElementById('loadXYZ').addEventListener('click', loadPDBFiles);
document.getElementById('playButton').addEventListener('click', playFrames);
document.getElementById('stopButton').addEventListener('click', stopFrames);

// Auto-load files
loadPDBFiles();
