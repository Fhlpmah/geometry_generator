// --- Global State and Constants ---
let scene, camera, renderer, controls;
let container;
let currentCoords = null; // Store successful coordinates for CSV export
const API_BASE_URL = 'http://127.0.0.1:5000'; // Assuming Flask runs on default port
let MODULE_SIZE = { x: 2.75, y: 2.75, z: 3.0 };
let BLOCK_COLORS = {};

// --- Helper Functions ---

function updateConsole(message, isError = false) {
    const log = document.getElementById('consoleLog');
    const timestamp = new Date().toLocaleTimeString();
    log.innerHTML = `<span style="color: ${isError ? 'var(--fail)' : 'var(--pass)'}">[${timestamp}]</span> ${message}`;
    log.scrollTop = log.scrollHeight;
}

function updateRulesLog(logData) {
    const rulesList = document.getElementById('rulesList');
    rulesList.innerHTML = ''; // Clear previous log

    logData.forEach(item => {
        const li = document.createElement('li');
        const statusClass = item.status === 'PASS' ? 'log-pass' : 
                           item.status === 'FAIL' ? 'log-fail' : 
                           item.status === 'SEPARATOR' ? 'log-separator' : '';
        
        li.className = statusClass;

        if (item.status === 'SEPARATOR') {
             li.textContent = item.message;
        } else {
             li.textContent = `${item.rule}: ${item.message}`;
        }
        rulesList.appendChild(li);
    });
}

function updateAnalysis(analysis) {
    const list = document.getElementById('analysisList');
    const params = analysis.parameters;
    const cog = analysis.cog;
    const mainFront = analysis.main_front;

    list.innerHTML = `
        <li>W_max: ${params.W_max || 'N/A'}</li>
        <li>L_max: ${params.L_max || 'N/A'}</li>
        <li>H_max: ${params.H_max || 'N/A'}</li>
        <li>Volume: ${params.Volume_V || 'N/A'}</li>
        <li>COG: (${cog.X ? cog.X.toFixed(2) : 'N/A'}, ${cog.Y ? cog.Y.toFixed(2) : 'N/A'}, ${cog.Z ? cog.Z.toFixed(2) : 'N/A'}) m</li>
        <li>Main Front: ${mainFront || 'N/A'}</li>
    `;
}

// --- Three.js Visualization ---

function initThree() {
    container = document.getElementById('three-container');
    const width = container.clientWidth;
    const height = container.clientHeight;

    // 1. Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1e293b);

    // 2. Camera
    camera = new THREE.PerspectiveCamera(45, width / height, 1, 1000);
    camera.position.set(20, 20, 20);

    // 3. Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);

    // 4. Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; // smooth rotation
    controls.dampingFactor = 0.05;

    // 5. Lighting
    scene.add(new THREE.AmbientLight(0x404040));
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
    directionalLight.position.set(10, 15, 10);
    scene.add(directionalLight);

    // 6. Grid Helper (Represents the 5x5 base in meters)
    const gridSize = 5 * MODULE_SIZE.x; // 5 modules * 2.75m/module
    const gridDivisions = 5;
    const gridHelper = new THREE.GridHelper(gridSize, gridDivisions, 0x475569, 0x475569);
    gridHelper.position.y = -0.01; // Place slightly below blocks
    gridHelper.material.transparent = true;
    gridHelper.material.opacity = 0.5;
    scene.add(gridHelper);

    // 7. Axes Helper (Optional: to show coordinate system)
    scene.add(new THREE.AxesHelper(10));

    // 8. Animation Loop
    animate();
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

function clearScene() {
    // Remove all objects except lighting, grid, and axes helper
    const objectsToKeep = [scene.children[0], scene.children[1], scene.children[2], scene.children[3]]; // Ambient, Directional, Grid, Axes
    scene.children.slice().forEach(object => {
        if (!objectsToKeep.includes(object)) {
            scene.remove(object);
        }
    });
}


function visualizeBlocks(coords, analysis) {
    clearScene();

    const group = new THREE.Group();

    // 1. Plot all blocks
    coords.forEach(block => {
        // Calculate physical dimensions and start coordinates (0-based)
        const dx_phys = block.dx * MODULE_SIZE.x;
        const dy_phys = block.dy * MODULE_SIZE.y;
        const dz_phys = block.dz * MODULE_SIZE.z;

        // Start coordinates: (Module_Index - 1) * Module_Size
        const x_start = (block.x - 1) * MODULE_SIZE.x;
        const y_start = (block.y - 1) * MODULE_SIZE.y;
        const z_start = (block.z - 1) * MODULE_SIZE.z;
        
        const colorHex = BLOCK_COLORS[block.type];

        const geometry = new THREE.BoxGeometry(dx_phys, dz_phys, dy_phys);
        const material = new THREE.MeshPhongMaterial({ 
            color: new THREE.Color(colorHex), 
            transparent: true, 
            opacity: 0.7 
        });
        const cube = new THREE.Mesh(geometry, material);

        // Position the cube based on its center
        cube.position.set(
            x_start + dx_phys / 2,
            z_start + dz_phys / 2, // Z in Python is Y/Height in Three.js
            y_start + dy_phys / 2  // Y in Python is Z/Depth in Three.js
        );
        group.add(cube);
    });

    // 2. Plot Center of Gravity (COG) (Topic 5)
    const cog = analysis.cog;
    const cogGeometry = new THREE.SphereGeometry(0.5, 32, 32);
    const cogMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 }); // Red
    const cogSphere = new THREE.Mesh(cogGeometry, cogMaterial);
    // Z in Python is Y/Height in Three.js
    cogSphere.position.set(cog.X, cog.Z, cog.Y); 
    group.add(cogSphere);
    
    // 3. Plot Main Front Indicator (Topic 6)
    const mainFront = analysis.main_front;
    const mainFrontColor = 0x00ffff; // Cyan
    const maxPhysX = 5 * MODULE_SIZE.x;
    const maxPhysY = 5 * MODULE_SIZE.y;
    
    // Create an arrow to indicate the direction of the main front
    if (mainFront !== 'N/A') {
        let directionVector = new THREE.Vector3(0, 0, 0);
        let arrowPos = new THREE.Vector3(maxPhysX / 2, 0, maxPhysY / 2);
        
        switch (mainFront) {
            case 'X+': // Facing +X
                directionVector.set(1, 0, 0);
                arrowPos.x = maxPhysX;
                break;
            case 'X-': // Facing -X
                directionVector.set(-1, 0, 0);
                arrowPos.x = 0;
                break;
            case 'Y+': // Facing +Y (which is +Z in Three.js)
                directionVector.set(0, 0, 1);
                arrowPos.z = maxPhysY;
                break;
            case 'Y-': // Facing -Y (which is -Z in Three.js)
                directionVector.set(0, 0, -1);
                arrowPos.z = 0;
                break;
        }
        
        // Place the arrow a bit above the ground
        arrowPos.y = 5; 

        const arrowHelper = new THREE.ArrowHelper(directionVector, arrowPos, 4, mainFrontColor, 1.5, 1);
        group.add(arrowHelper);
    }


    scene.add(group);
    controls.target.set(maxPhysX / 2, maxPhysY / 2, maxPhysY / 2); // Center the view on the grid
    controls.update();
}

// --- Event Handlers (Topic 2, 3, 4, 5, 6) ---

async function handleGenerate() {
    const comfort = document.getElementById('comfortInput').value;
    const transparent = document.getElementById('transparentInput').value;
    const opaque = document.getElementById('opaqueInput').value;

    if (comfort < 0 || transparent < 0 || opaque < 0) {
        updateConsole("Input counts cannot be negative.", true);
        return;
    }
    
    document.getElementById('generateBtn').disabled = true;
    document.getElementById('exportCsvBtn').disabled = true;
    updateConsole("Generating configuration (up to 1000 attempts)...");
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comfort, transparent, opaque })
        });

        const data = await response.json();
        updateConsole(data.console, !data.success);
        updateRulesLog(data.log);

        if (data.success) {
            currentCoords = data.coords;
            visualizeBlocks(data.coords, data.analysis);
            updateAnalysis(data.analysis);
            document.getElementById('exportCsvBtn').disabled = false;
        } else {
            currentCoords = null;
            clearScene();
            updateAnalysis({});
        }

    } catch (error) {
        updateConsole(`API Error: ${error.message}. Ensure the Flask server (app.py) is running on ${API_BASE_URL}.`, true);
    } finally {
        document.getElementById('generateBtn').disabled = false;
    }
}

function handleReset() {
    document.getElementById('comfortInput').value = 5;
    document.getElementById('transparentInput').value = 3;
    document.getElementById('opaqueInput').value = 1;
    clearScene();
    currentCoords = null;
    document.getElementById('exportCsvBtn').disabled = true;
    document.getElementById('rulesList').innerHTML = '';
    updateAnalysis({});
    updateConsole("Input fields reset to default (5, 3, 1). Scene cleared.");
}

async function handleExportCsv() {
    if (!currentCoords) {
        updateConsole("No valid configuration to export.", true);
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/export_csv`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ coords: currentCoords })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'block_coordinates.csv';
        document.body.appendChild(a);
        a.click();
        a.remove();
        updateConsole("Coordinates exported successfully to block_coordinates.csv");

    } catch (error) {
        updateConsole(`Export Error: ${error.message}.`, true);
    }
}

// --- Initialization ---

async function loadConstants() {
    try {
        const response = await fetch(`${API_BASE_URL}/constants`);
        const data = await response.json();
        
        // Update global constants
        MODULE_SIZE = data.MODULE_SIZE;
        BLOCK_COLORS = data.BLOCK_COLORS;

        // Initialize Three.js after loading constants
        initThree();
        updateConsole("System ready. Flask API constants loaded. Use Generate to start.");

    } catch (error) {
        updateConsole(`CRITICAL: Could not connect to Flask API at ${API_BASE_URL}. Please start the Python server first.`, true);
        // Fallback constants if API is down, to at least allow interface rendering
        initThree(); 
    }
}

window.onload = loadConstants;