# Architectural Geometry Generatior

A backend and frontend system for generating and validating 3D architectural geometries.
The system supports automatic block placement, rule-based validation, CSV exporting, and real-time 3D visualization through a Three.js interface.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Overview

This project provides a constraint-based geometry generator using Python (Flask) for the backend and React for the frontend.
Two generation modes are available:
1. Random Mode – generates all blocks using a backtracking algorithm.
2. Correct Mode – loads a pre-validated base geometry from CSV and places additional transparent blocks.

All generated geometries can be visualized in 3D and exported as CSV.

## Features

- Geometry generation with backtracking algorithms
- Frontend 3D visualization using Three.js
- REST API for programmatic access
- CSV export for external use

Validation system covering architectural constraints

## Set-up

### Prerequisites

- Python 3.8+
- pip 24+
- git 2.50

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Fhlpmah/geometry_generator.git
cd <the_project_folder>
```

### Running the Application

1. **Start Backend (Flask API)**
```bash
cd back_end
source venv/bin/activate      # Windows: venv\Scripts\activate
python3 app.py  
```

The backend will run at: `http://localhost:5000`

2. **Open the Frontend**
The frontend is plain HTML/JS, so there are two options:

Option A — Open directly in browser (if it works)
- Go to the `front_end` folder
- Open `index.html` by double-clicking it. It will open in (Chrome / Firefox / Edge)

Option B — Recommended: Use Live Server
If your browser blocks file paths (CORS), use VS Code:
1. Open the project in VS Code
2. Install the Live Server extension
3. Right-click `index.html
4. Select “Open with Live Server”

Frontend will open at: `http://localhost:5500`

## 🎯 Usage

### Generate Geometry

1. **Select Comfort Zones**: Choose the number of comfort zones by typing
2. **Select Transparent Buffer**: Choose the number of transparent buffers by typing
3. **Select Opaque Buffer**: Choose the number of opaque buffers by typing
4. **Click "Generate Geometry"**: View results in 3D

### Blocks Generation Explained

- Generates blocks randomly using backtracking based on how much blocks for each type of blocks.
- Fast generation (<5 seconds)
- Rules validation while backtracking executing.

## 📁 Project Structure

```
Geometry-Generation/
├── back_end/
│   ├── api.py                      # Flask REST API
│   ├── block_generation.py         # Backtracking, Validation Algorithm
│   ├── main.js                     # Main Website Component
├── frontend/
│   ├── index.html                  # Website Interface
│   ├── style.css                   # Website Interface Style
├── .gitignore
└── README.md                       # This file
```

## Technologies

### Backend
- **Flask**: REST API framework
- **Python 3.8+**: Core language
- **CSV**: Data storage for validated geometries

### Frontend
- **Three.js** (via @react-three/fiber): 3D visualization

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Developers

- **Minho Choi** - [-](-)
- **Fhilipus Mahendra** - [@fhlpmah](https://github.com/fhlpmah)
- **Danial Sadad** - [@danialsadad](https://github.com/danialsadad)
- **Zhao Yawen** - [-](-)

## Acknowledgments

- Three.js community for 3D rendering capabilities
- Flask community for lightweight API framework
