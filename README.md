# 🏗️ Modular Family House Geometry Generator

An intelligent system for generating and validating 3D architectural geometries using constraint satisfaction and backtracking algorithms. Features dual generation modes: **Random Mode** (fast random placement) and **Correct Mode** (CSV-based validated geometries with customizable transparent buffers).

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-18.3-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Features

- **Dual Generation Modes**:
  - 🎲 **Random Mode**: Generate all blocks randomly using backtracking algorithm
  - ✅ **Correct Mode**: Load validated base geometry from CSV + place transparent buffers intelligently
- **Interactive 3D Visualization**: Real-time Three.js rendering with color-coded blocks
- **User-Controlled Transparency**: Select 1, 2, or 3 transparent buffers via radio buttons
- **Fast Generation**: Correct mode generates in <1 second (vs 10-180s with full backtracking)
- **Comprehensive Validation**: 20+ architectural rules with detailed violation reports
- **REST API**: Clean Flask API with JSON responses

## 📦 Architecture

### Block Types
- **Comfort Zones** (Green): 5 blocks, 1×1×1 cells each
- **Transparent Buffers** (Blue): 1-3 blocks (user-selectable), 1×1×1 cells each
- **Opaque Buffer** (Orange): 1 block, 1×1×1 cells

### Grid System
- **Dimensions**: 8×4×3 cells (X × Y × Z)
- **Cell Size**: 2.75m × 2.75m × 3m
- **Total Blocks**: 7-9 blocks depending on transparent buffer selection

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/hoangtrietdev/Geometry-Generation.git
cd Geometry-Generation
```

2. **Setup Backend**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Setup Frontend**:
```bash
cd ../frontend
npm install
```

### Running the Application

1. **Start Backend** (Terminal 1):
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python3 api.py
```
Backend runs on `http://localhost:5001`

2. **Start Frontend** (Terminal 2):
```bash
cd frontend
npm start
```
Frontend opens at `http://localhost:3000`

## 🎯 Usage

### Generate Geometry

1. **Select Transparent Buffers**: Choose 1, 2, or 3 transparent buffers using radio buttons
2. **Choose Mode**:
   - ⬜ **Unchecked (Correct Mode)**: Loads validated geometry from CSV + adds random transparent buffers
   - ✅ **Checked (Random Mode)**: Generates all blocks randomly
3. **Click "Generate Geometry"**: View results in 3D

### Generation Modes Explained

#### 🎲 Random Mode (Checkbox Checked)
- Generates **all blocks** randomly using backtracking
- Fast generation (<5 seconds)
- May violate some architectural rules
- Good for exploration and testing

#### ✅ Correct Mode (Checkbox Unchecked) 
- Loads **base geometry** from `full_data.csv` (5 Comfort + 1 Opaque)
- Randomly places **transparent buffers** adjacent to comfort zones
- Ultra-fast (<1 second)
- Base geometry is pre-validated
- Perfect for production use

## 📁 Project Structure

```
Geometry-Generation/
├── backend/
│   ├── api.py                      # Flask REST API
│   ├── models.py                   # Data structures (Block, Geometry)
│   ├── backtracking.py             # Backtracking algorithm
│   ├── csv_geometry_loader.py      # CSV loader + transparent placement
│   ├── assembly_rules.py           # Assembly validation rules
│   ├── validation.py               # Geometry validation
│   ├── descriptors.py              # Architectural descriptors
│   ├── full_data.csv               # Pre-validated geometries
│   ├── requirements.txt            # Python dependencies
│   └── README.md                   # Backend documentation
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── GenerateSection.tsx # Generation UI + controls
│   │   │   └── GeometryViewer.tsx  # 3D visualization
│   │   ├── App.tsx                 # Main app component
│   │   └── index.tsx               # Entry point
│   ├── package.json                # Node dependencies
│   └── README.md                   # Frontend documentation
├── .gitignore
└── README.md                       # This file
```

## 🔌 API Endpoints

### Generate Geometry
```http
POST /api/generate
Content-Type: application/json

{
  "mode": "correct",           # "correct" or "random"
  "comfort_zones": 5,          # Fixed at 5
  "transparent_buffers": 2,    # 1, 2, or 3 (user-selected)
  "opaque_buffers": 1          # Fixed at 1
}
```

**Response**:
```json
{
  "success": true,
  "mode": "correct",
  "csv_data": "1;0;0;0;1;0;0;...",
  "validation": {
    "is_valid": true,
    "violated_rules": [],
    "warnings": []
  },
  "generation_time": 0.12,
  "note": "Base geometry loaded from CSV (ID: 78), transparent buffers placed randomly",
  "source": "csv_with_random_transparent",
  "csv_geometry_id": 78
}
```

## 🛠️ Technologies

### Backend
- **Flask**: REST API framework
- **Python 3.8+**: Core language
- **CSV**: Data storage for validated geometries

### Frontend
- **React 18.3**: UI framework
- **TypeScript**: Type-safe development
- **Three.js** (via @react-three/fiber): 3D visualization
- **Axios**: HTTP client

## 📊 Performance

| Mode | Generation Time | Validation | Use Case |
|------|----------------|------------|----------|
| **Correct** | <1 second | Pre-validated base | Production, fast results |
| **Random** | <5 seconds | May violate rules | Exploration, testing |

## 🧪 Testing

### Backend Tests
```bash
cd backend
python3 csv_geometry_loader.py  # Test CSV loader
```

### Manual Testing
1. Start both backend and frontend
2. Test Correct Mode:
   - Select 1 transparent buffer → Should show 7 blocks
   - Select 2 transparent buffers → Should show 8 blocks
   - Select 3 transparent buffers → Should show 9 blocks
3. Test Random Mode:
   - Check "Generate Random Geometry"
   - Should generate all blocks randomly

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't connect
```bash
# Check backend is running
curl http://localhost:5001/api/generate

# Check CORS is enabled in api.py
# Verify CORS(app) is present
```

### 3D viewer shows blocks too large
- **Issue**: Blocks appear as 2×2 cubes instead of 1×1
- **Fix**: Ensure both `models.py` (backend) and `GeometryViewer.tsx` (frontend) use 1×1×1 dimensions

## 📝 Configuration

### Backend Configuration
Edit `backend/api.py`:
```python
# Port configuration (line ~535)
app.run(host='0.0.0.0', port=5001, debug=True)

# Grid size (line ~10 in backtracking.py)
max_x, max_y, max_z = 8, 4, 3
```

### Frontend Configuration
Edit `frontend/src/components/GenerateSection.tsx`:
```typescript
// API URL (line ~20)
const API_URL = 'http://localhost:5001';
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Authors

- **Hoang Triet** - [@hoangtrietdev](https://github.com/hoangtrietdev)

## 🙏 Acknowledgments

- Three.js community for 3D rendering capabilities
- Flask community for lightweight API framework
- React Three Fiber for seamless React + Three.js integration

## 📧 Support

For issues and questions:
- Open an issue on [GitHub Issues](https://github.com/hoangtrietdev/Geometry-Generation/issues)
- Email: [your-email@example.com]

---

**Made with ❤️ for architectural geometry generation**
