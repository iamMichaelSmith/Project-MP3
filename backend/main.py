from flask import Flask, request, jsonify
import yt_dlp
import boto3
import os
import threading
import requests

app = Flask(__name__)

# AWS S3 configuration
S3_BUCKET = "your-s3-bucket-name"
s3_client = boto3.client('s3')

@app.route('/convert', methods=['POST'])
def convert():
    # Parse the request data
    data = request.get_json()
    youtube_url = data.get('youtubeUrl')

    if not youtube_url:
        return jsonify({'error': 'YouTube URL is required'}), 400

    try:
        # Download and convert YouTube video to MP3
        output_file = "/tmp/output.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_file,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        # Upload the file to S3
        s3_key = "output.mp3"
        s3_client.upload_file(output_file, S3_BUCKET, s3_key)

        # Generate pre-signed URL for download
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=3600
        )

        # Return the pre-signed URL to the client
        return jsonify({'downloadUrl': presigned_url}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Test script to send a request to the Flask app
def run_test():
    print("\n--- Running Test ---")
    test_url = "http://127.0.0.1:5000/convert"
    payload = {"youtubeUrl": "https://www.youtube.com/watch?v=fGIMde2N2g0"}

    try:
        response = requests.post(test_url, json=payload)
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())
    except Exception as e:
        print("Test failed:", str(e))


if __name__ == '__main__':
    # Start Flask app in a separate thread to allow inline testing
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()

    # Run the test after the server starts
    run_test()
from flask import Flask, request, jsonify
import yt_dlp
import boto3
import os

app = Flask(__name__)

# AWS S3 configuration
S3_BUCKET = "your-s3-bucket-name"
s3_client = boto3.client('s3')

@app.route('/convert', methods=['POST'])
def convert():
    # Parse the request data
    data = request.get_json()
    youtube_url = data.get('youtubeUrl')

    if not youtube_url:
        return jsonify({'error': 'YouTube URL is required'}), 400

    try:
        # Download and convert YouTube video to MP3
        output_file = "/tmp/output.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_file,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        # Upload the file to S3
        s3_key = "output.mp3"
        s3_client.upload_file(output_file, S3_BUCKET, s3_key)

        # Generate pre-signed URL for download
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=3600
        )

        # Return the pre-signed URL to the client
        return jsonify({'downloadUrl': presigned_url}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
