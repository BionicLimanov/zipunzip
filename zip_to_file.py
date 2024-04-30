from flask import Flask, request, jsonify, send_file
import zipfile
import os

app = Flask(__name__)

@app.route('/must-A-nice', methods=['POST'])
def unzip_file():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({'error': 'Request data must be in JSON format'}), 400

    # Extract the JSON data from the request
    json_data = request.json

    # Check if the JSON data contains the list of file paths
    if 'files' not in json_data:
        return jsonify({'error': 'No list of file paths found in JSON data'}), 400

    # Extract the path to the zipped file from the list of file paths
    zip_file_paths = json_data['files']

    # Check if the list of file paths is empty
    if not zip_file_paths:
        return jsonify({'error': 'No file paths found in the list'}), 400

    extracted_folders = []
    for zip_file_path in zip_file_paths:
        # Check if the specified file exists
        if not os.path.exists(zip_file_path):
            return jsonify({'error': f'File not found at path: {zip_file_path}'}), 404

        # Extract the directory containing the JSON file
        base_directory = os.path.dirname(zip_file_path)

        # Extract the zip file to the base directory
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(base_directory)

        extracted_folders.append(base_directory)

    # Return the list of paths to the extracted folders
    return jsonify({'extracted_folder_paths': extracted_folders})

@app.route('/download/<path:filename>', methods=['GET'])
def download_file2(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
