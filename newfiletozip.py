from flask import Flask, request, jsonify, send_file
import requests
import zipfile
import os
import shutil
from urllib.parse import urlparse, unquote
import random
import string
import concurrent.futures
import threading

app = Flask(__name__)

def download_file(url, dest_folder):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            file_name = os.path.basename(urlparse(url).path)
            file_path = os.path.join(dest_folder, file_name)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return file_path
        else:
            return None
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return None

def zip_files(urls):
    temp_dir = 'temp_zip'
    os.makedirs(temp_dir, exist_ok=True)

    downloaded_files = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_file, url, temp_dir) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            file_path = future.result()
            if file_path:
                downloaded_files.append(file_path)

    if not downloaded_files:
        return jsonify({'error': 'Failed to download any files'}), 500

    try:
        random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        zip_file_name = f'zipped_files_{random_name}.zip'
        with zipfile.ZipFile(zip_file_name, 'w') as zipf:
            for file_path in downloaded_files:
                zipf.write(file_path, os.path.basename(file_path))

        userzip_folder = 'user/dataupload'
        os.makedirs(userzip_folder, exist_ok=True)
        shutil.move(zip_file_name, os.path.join(userzip_folder, zip_file_name))

        download_link = request.url_root + 'download/' + zip_file_name

        # Schedule deletion of the zip file after 3 seconds
        threading.Timer(1, delete_file, args=[os.path.join(userzip_folder, zip_file_name)]).start()

        return jsonify({'download_link': download_link})
    except Exception as e:
        return jsonify({'error': f'Failed to zip files: {str(e)}'}), 500
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

@app.route('/zip', methods=['POST'])
def zip_files_route():
    if not request.is_json:
        return jsonify({'error': 'Request data must be in JSON format'}), 400
    json_data = request.json
    file_urls = json_data.get('files', [])
    if not file_urls:
        return jsonify({'error': 'No files provided in the request'}), 400
    return zip_files(file_urls)

@app.route('/download/<path:filename>', methods=['GET'])
def download_file2(filename):
    file_path = os.path.join('userzip', filename)
    response = send_file(file_path, as_attachment=True)
    
    # Schedule deletion of the downloaded file after sending
    threading.Timer(1, delete_file, args=[file_path]).start()
    
    return response

if __name__ == '__main__':
    app.run()
