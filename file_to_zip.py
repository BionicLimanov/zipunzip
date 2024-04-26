from flask import Flask, request, jsonify
import zipfile
import os

app = Flask(__name__)

@app.route('/zip_files', methods=['POST'])
def zip_files():
    # Check if the request contains files
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files found in the request'}), 400
    
    files = request.files.getlist('files[]')
    
    # Create a temporary directory to store the files
    temp_dir = 'foldertest'
    os.makedirs(temp_dir, exist_ok=True)
    
    # Save the files to the temporary directory
    file_paths = []
    for file in files:
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        file_paths.append(file_path)
    
    # Create a zip file
    zip_file_name = 'zipped_files.zip'
    with zipfile.ZipFile(zip_file_name, 'w') as zipf:
        for file_path in file_paths:
            zipf.write(file_path, os.path.basename(file_path))
    
    # Return the zip file
    return jsonify({'zip_file': zip_file_name}), 200

if __name__ == '__main__':
    app.run(debug=True)
