from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
from io import StringIO
from back_end.block_generation import generate_configuration_api, CONSTANTS

app = Flask(__name__)
CORS(app) # Enable CORS for frontend development

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    comfort = int(data.get('comfort', 5))
    transparent = int(data.get('transparent', 3))
    opaque = int(data.get('opaque', 1))
    
    result = generate_configuration_api(comfort, transparent, opaque)
    return jsonify(result)

@app.route('/constants', methods=['GET'])
def get_constants():
    return jsonify(CONSTANTS)

@app.route('/export_csv', methods=['POST'])
def export_csv():
    data = request.get_json()
    coords = data.get('coords', [])
    
    if not coords:
        return jsonify({"error": "No configuration data provided."}), 400

    # Create a DataFrame from the coordinate list
    df = pd.DataFrame(coords)
    
    # Select and reorder columns for the required CSV format (Base coords: x, y, z)
    df_export = df[['id', 'type', 'x', 'y', 'z', 'dx', 'dy', 'dz']]
    df_export.columns = ['Block ID', 'Type', 'X_mod (1-based)', 'Y_mod (1-based)', 'Z_mod (1-based)', 'DX_mod', 'DY_mod', 'DZ_mod']
    
    # Save to CSV string
    csv_buffer = StringIO()
    df_export.to_csv(csv_buffer, index=False)
    
    # Send the CSV as a file attachment
    csv_buffer.seek(0)
    return send_file(
        StringIO(csv_buffer.getvalue()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='block_coordinates.csv'
    )

if __name__ == '__main__':
    # To run: flask --app app run
    # OR: app.run(debug=True)
    print("Run the server using: flask --app app run")
    # For a persistent URL/run environment, execute the command in your environment's shell.
    # Running app.run() directly here may not work in all notebook/code execution environments.