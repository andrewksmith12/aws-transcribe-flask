from flask import Flask, render_template, session, request, redirect, url_for, escape
from flask_session import Session
import AWSfunctions
import pyperclip
import os
from werkzeug.utils import secure_filename

uploads_bucket = "python-upload-target"
transcriptions_bucket = "python-transcribe-target"

app = Flask(__name__)
Session(app)


ALLOWED_EXTENSIONS = ['mp3', 'mp4', 'flac', 'ogg', 'webm', 'amr', 'wav']
app.config['UPLOAD_FOLDER'] = 'uploads'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    items = AWSfunctions.get_file_list(transcriptions_bucket)
    return render_template('index.html', fileList = items, prefix="s3://"+transcriptions_bucket)

@app.route('/itemDetail/<string:fileName>', methods=['GET'])
def itemDetail(fileName):
    print(fileName)
    body = AWSfunctions.get_file(transcriptions_bucket, fileName)
    pyperclip.copy(str(body))
    return render_template("itemDetail.html", body=body)

# I'd rather not have this as a seperate function... 
@app.route('/itemDetail/medical/<string:fileName>', methods=['GET'])
def parseMedicalKey(fileName):
    fileName = "medical/"+fileName
    body = AWSfunctions.get_file(transcriptions_bucket, fileName)
    pyperclip.copy(str(body))
    return render_template("itemDetail.html", body=body)

@app.route('/upload', methods=['GET', 'POST'])
def uploadFile():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('uploadFile'))
        file = request.files['file']
        if file.filename == '':
            return redirect(url_for('uploadFile'))
        if file and allowed_file(file.filename):
            file.filename = secure_filename(file.filename)
            AWSfunctions.upload_fileObject(file, uploads_bucket)
            s3Location = str("s3://"+uploads_bucket+"/"+file.filename)
            result = AWSfunctions.create_transcript(s3Location, transcriptions_bucket, str(file.filename))
            print(result)
            return redirect(url_for('index'))
        else:
            return "Invalid File."
    if request.method == 'GET':
        return render_template('uploadItem.html', allowedTypes = ALLOWED_EXTENSIONS)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)