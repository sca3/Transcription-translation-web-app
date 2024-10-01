from flask import Flask, request, send_file, render_template
from vulavula import VulavulaClient
from vulavula.common.error_handler import VulavulaError
import os
import requests
import time 
from retry_requests import retry


app = Flask(__name__)

# Folder where audio files are storedl
AUDIO_FOLDER = 'audio_files'

@app.route('/')
def index():   
    return render_template('index.HTML')

@app.route('/get_translation')
def GetTranslation():
    VULAVULA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjM2ZGQ4NTgyNDRkNDQ4NmI5MzM3MTBiOGU0OGMwMTIyIiwiY2xpZW50X2lkIjo3MCwicmVxdWVzdHNfcGVyX21pbnV0ZSI6MCwibGFzdF9yZXF1ZXN0X3RpbWUiOm51bGx9.JKe-hoIrlDX5FH4b2eJPdLyi_OLVhDXLqXVYAUmz0Ro"

    client = VulavulaClient(VULAVULA_TOKEN)
    #TRANSPORT_URL = "https://vulavula-services.lelapa.ai/api/v1/transport/file-upload"

    #TRANSCRIBE_URL = "https://vulavula-services.lelapa.ai/api/v1/transcribe/process/"

    WEBHOOK_URL="https://webhook.site/b538c244-28b5-4acf-8fe9-d807470c7b4d"

    FILE_TO_TRANSCRIBE = "audio_files/Recording (2).mp3"

    try:
        upload_id, transcription_result = client.transcribe(FILE_TO_TRANSCRIBE, webhook=WEBHOOK_URL)
        print("Acknowledgement:", transcription_result) #A success message, data is sent to webhook
    except VulavulaError as e:
        print("An error occurred:", e.message)
        if 'details' in e.error_data:
            print("Error Details:", e.error_data['details'])
        else:
            print("No additional error details are available.")
    except Exception as e:
        print("An unexpected error occurred:", str(e))
        
    while client.get_transcribed_text(upload_id)['message'] == "Item has not been processed.":
        time.sleep(5)
        print("Waiting for transcribe to complete...")
    RES = client.get_transcribed_text(upload_id)
    
    Langs = ['zul_Latn', 'nso_Latn', 'afr_Latn', 'tso_Latn']
    response = []
    for lang in Langs:
        
        print(lang)
        translation_data = {
            "input_text": RES['text'],
            "source_lang": "eng_Latn",
            "target_lang": lang
        }
    
        translation_result = client.translate(translation_data)
        
        response.append({
            "lang" : lang,
            "value" : translation_result['translation'][0]['translation_text']
        })
    
    return render_template('result.HTML', value = response )

@app.route('/get_audio', methods=['POST'])
def get_audio():
    filename = request.form['filename']
    file_path = os.path.join(AUDIO_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return f"File '{filename}' not found", 404

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/get_audio', methods=['POST'])
def get_audio():
    filename = request.form.get('filename')
    if not filename:
        return "No filename provided", 400

    file_path = os.path.join(AUDIO_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return f"File '{filename}' not found", 404


if __name__ == '__main__':
    app.run(debug=True)