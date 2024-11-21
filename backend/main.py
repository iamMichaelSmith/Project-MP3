from flask import Flask, request, jsonify
import yt_dlp
import boto3
import os
import requests
import uuid  # For unique file names

app = Flask(__name__)

# AWS S3 configuration
S3_BUCKET = "project-mp3-files"
s3_client = boto3.client('s3', region_name='us-east-1')

# Path to ffmpeg binary
FFMPEG_LOCATION = "C:/Program Files/ffmpeg-2024-11-18-git-970d57988d-essentials_build/bin"

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    youtube_url = data.get('youtubeUrl')

    if not youtube_url:
        return jsonify({'error': 'YouTube URL is required'}), 400

    try:
        output_file = "/tmp/output.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_file,
            'ffmpeg_location': FFMPEG_LOCATION,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        s3_key = f"{uuid.uuid4()}.mp3"
        s3_client.upload_file(output_file, S3_BUCKET, s3_key)

        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=3600
        )

        return jsonify({'downloadUrl': presigned_url}), 200

    except yt_dlp.utils.DownloadError as e:
        return jsonify({'error': f"YouTube download failed: {str(e)}"}), 500
    except boto3.exceptions.Boto3Error as e:
        return jsonify({'error': f"Error uploading to S3: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
