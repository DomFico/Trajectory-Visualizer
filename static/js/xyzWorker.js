// xyzWorker.js

// Parse XYZ data in the Web Worker
onmessage = function(event) {
    const xyzData = event.data.trim().split(/\r?\n/);
    const atomCount = parseInt(xyzData[0].trim());

    if (isNaN(atomCount) || atomCount <= 0 || xyzData.length < atomCount + 2) {
        postMessage({ error: 'Invalid XYZ format.' });
        return;
    }

    const atoms = [];
    for (let i = 2; i < atomCount + 2; i++) {
        const [elem, x, y, z] = xyzData[i].trim().split(/\s+/);
        atoms.push({
            elem: elem,
            x: parseFloat(x),
            y: parseFloat(y),
            z: parseFloat(z)
        });
    }

    postMessage(atoms);  // Send parsed atoms back to the main thread
};
