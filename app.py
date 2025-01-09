from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pytubefix import YouTube

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:3000"}})


@app.route('/check_url', methods=['POST'])
def check_url():
    data = request.get_json()
    url = data.get('url')

    yt = YouTube(url)
    streams_info = {
        'title': yt.title,
        'thumbnail_url': yt.thumbnail_url,
        'progressive': [],
        'adaptive_video': [],
        'audio': []
    }

    # Collect progressive streams (Video + Audio)
    for stream in yt.streams.filter(progressive=True):
        filesize_mb = stream.filesize / (1024 * 1024) if stream.filesize else 'N/A'
        streams_info['progressive'].append({
            'itag': stream.itag,
            'resolution': stream.resolution,
            'filesize': f"{filesize_mb:.2f}" if filesize_mb != 'N/A' else 'N/A'
        })

    # Collect adaptive video streams (Video only)
    for stream in yt.streams.filter(adaptive=True, only_video=True):
        filesize_mb = stream.filesize / (1024 * 1024) if stream.filesize else 'N/A'
        streams_info['adaptive_video'].append({
            'itag': stream.itag,
            'resolution': stream.resolution,
            'filesize': f"{filesize_mb:.2f}" if filesize_mb != 'N/A' else 'N/A'
        })

    # Collect audio streams (Audio only)
    for stream in yt.streams.filter(only_audio=True):
        filesize_mb = stream.filesize / (1024 * 1024) if stream.filesize else 'N/A'
        streams_info['audio'].append({
            'itag': stream.itag,
            'format': 'mp3',  # Explicitly set format to mp3
            'filesize': f"{filesize_mb:.2f}" if filesize_mb != 'N/A' else 'N/A'
        })

    return jsonify(streams_info)


@app.route('/download/<int:itag>', methods=['GET'])
def download(itag):
    url = request.args.get('url')
    ext = request.args.get('ext', 'video')  # Default to video if not specified

    yt = YouTube(url)  
    stream = yt.streams.get_by_itag(itag)
    
    # Download video/audio to a temporary location
    download_path = stream.download()

    # Change the file extension if it's audio
    if ext == 'mp3':
        download_path = f"{download_path[:-4]}.mp3"  # Change to mp3

    return send_file(download_path, as_attachment=True)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
