from flask import Flask, request, jsonify
import zipfile
import os

app = Flask(__name__)

@app.route('/unzip_file', methods=['POST'])
def unzip_file():
    # Check if the request contains a file
    if 'file' not in request.files:
        return jsonify({'error': 'No file found in the request'}), 400
    
    zip_file = request.files['file']
    
    # Save the zip file to a temporary location
    temp_zip_path = 'temp.zip'
    zip_file.save(temp_zip_path)
    
    # Extract the zip file
    with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
        # Extract all contents to a folder with the same name as the zip file
        zip_file_name = os.path.splitext(zip_file.filename)[0]
        extract_path = zip_file_name
        os.makedirs(extract_path, exist_ok=True)
        zip_ref.extractall(extract_path)
    
    # Remove the temporary zip file
    os.remove(temp_zip_path)
    
    return jsonify({'message': f'Zip file "{zip_file_name}" has been successfully extracted'}), 200

if __name__ == '__main__':
    app.run(debug=True)
