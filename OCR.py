from flask import Flask, request, render_template, redirect, url_for
from paddleocr import PaddleOCR, draw_ocr
import cv2
import os
import pandas as pd
import re
from werkzeug.utils import secure_filename

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Setup PaddleOCR model
ocr_model = PaddleOCR(lang='en')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('display_results', filename=filename))
    return render_template('upload.html')

@app.route('/results/<filename>')
def display_results(filename):
    try:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        result = ocr_model.ocr(img_path)

        # Extracting detected components
        scores = [res[1][1] for res in result]

        texts = [res[1][0] for res, score in zip(result, scores) if score >= 0.9]
        boxes = [res[0] for res, score in zip(result, scores) if score >= 0.9]
        scores = [score for score in scores if score >= 0.9]

        values = []
        values.append(texts[4])
        values.append(texts[6])
        if texts[7] == 'Gender Country of Stay':
            if re.search(r'[0-9]', texts[14]):
                texts.pop(14)
                boxes.pop(14)
                scores.pop(14)

            if re.search(r'[a-zA-Z]', texts[12]):
                values.append(texts[8])
                values.append(texts[9])
                values.append(texts[13])
                values.append(texts[14])
                values.append(texts[17])
                values.append(texts[18])
                texts.pop(12)
                boxes.pop(12)
                scores.pop(12)
            else:
                values.append(texts[8])
                values.append(texts[9])
                values.append(texts[12])
                values.append(texts[13])
                values.append(texts[16])
                values.append(texts[17])
        else:
            if re.search(r'[0-9]', texts[15]):
                texts.pop(15)
                boxes.pop(15)
                scores.pop(15)

            if re.search(r'[a-zA-Z]', texts[13]):
                values.append(texts[9])
                values.append(texts[10])
                values.append(texts[14])
                values.append(texts[15])
                values.append(texts[18])
                values.append(texts[19])
                texts.pop(13)
                boxes.pop(13)
                scores.pop(13)
            else:
                values.append(texts[9])
                values.append(texts[10])
                values.append(texts[13])
                values.append(texts[14])
                values.append(texts[17])
                values.append(texts[18])

        headers = ['Name', 'Father Name / Husband Name', 'Gender', 'Country of Stay', 'Identity Number', 'Date of Birth', 'Date of Issue', 'Date of Expiry']

        return render_template('results.html', headers=headers, values=values)
    
    except Exception as e:
        error="Failed to detect data fields from your CNIC. Please try again."
        return render_template('error.html', error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
