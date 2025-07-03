import os
import subprocess
from flask import Flask, request, send_from_directory, jsonify, url_for

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
HLS_FOLDER = 'hls'
PREVIEW_NAME = 'preview.jpg'

# Définir la base URL ici (à adapter selon votre déploiement)
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(HLS_FOLDER, exist_ok=True)

def get_next_video_id():
    if not os.path.exists(HLS_FOLDER):
        return "video1"
    existing = [d for d in os.listdir(HLS_FOLDER) if os.path.isdir(os.path.join(HLS_FOLDER, d)) and d.startswith('video') and d[5:].isdigit()]
    nums = [int(d[5:]) for d in existing]
    next_num = max(nums) + 1 if nums else 1
    return f"video{next_num}"

def convert_mp4_to_hls(mp4_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    m3u8_path = os.path.join(output_dir, 'index.m3u8')
    command = [
        'ffmpeg', '-i', mp4_path,
        '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental',
        '-start_number', '0',
        '-hls_time', '10',
        '-hls_list_size', '0',
        '-f', 'hls',
        m3u8_path
    ]
    subprocess.run(command, check=True)
    # Générer une image de preview si elle n'existe pas déjà
    preview_path = os.path.join(output_dir, PREVIEW_NAME)
    if not os.path.exists(preview_path):
        try:
            subprocess.run([
                'ffmpeg', '-i', mp4_path, '-ss', '00:00:01.000', '-vframes', '1', preview_path
            ], check=True)
        except Exception:
            pass
    return m3u8_path

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = file.filename
    # Accepter tous les formats vidéo courants
    allowed_exts = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
    if not isinstance(filename, str):
        return jsonify({'error': 'Invalid filename'}), 400
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_exts:
        return jsonify({'error': f'Extension {ext} non supportée'}), 400
    mp4_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(mp4_path)
    video_id = get_next_video_id()
    hls_dir = os.path.join(HLS_FOLDER, video_id)
    try:
        convert_mp4_to_hls(mp4_path, hls_dir)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'hls_url': f'/hls/{video_id}/index.m3u8'})

@app.route('/hls/<video_id>/<path:filename>')
def stream(video_id, filename):
    hls_dir = os.path.join(HLS_FOLDER, video_id)
    return send_from_directory(hls_dir, filename)

@app.route('/videos', methods=['GET'])
def list_videos():
    videos = []
    for d in sorted(os.listdir(HLS_FOLDER)):
        if os.path.isdir(os.path.join(HLS_FOLDER, d)) and d.startswith('video') and d[5:].isdigit():
            num = int(d[5:])
            title = f"Video {num}"
            hls_url = f"{BASE_URL}/hls/{d}/index.m3u8"
            preview_path = os.path.join(HLS_FOLDER, d, PREVIEW_NAME)
            if os.path.exists(preview_path):
                preview_url = f"{BASE_URL}/hls/{d}/preview.jpg"
            else:
                preview_url = None
            vtt_filenames = ['index.vtt.m3u8', 'index_vtt.m3u8']
            vtt_found = None
            for vtt_filename in vtt_filenames:
                vtt_path = os.path.join(HLS_FOLDER, d, vtt_filename)
                if os.path.exists(vtt_path):
                    vtt_found = vtt_filename
                    break
            has_vtt = vtt_found is not None
            if has_vtt:
                hls_vtt = {
                    'url': f"{BASE_URL}/hls/{d}/{vtt_found}",
                    'filename': vtt_found
                }
            else:
                hls_vtt = {
                    'url': None,
                    'filename': None
                }
            videos.append({
                'id': d,
                'title': title,
                'hls_url': hls_url,
                'preview_url': preview_url,
                'hls_vtt': hls_vtt,
                'has_vtt': has_vtt
            })
    return jsonify(videos)

@app.route('/hls/<video_id>/preview.jpg')
def video_preview(video_id):
    hls_dir = os.path.join(HLS_FOLDER, video_id)
    return send_from_directory(hls_dir, PREVIEW_NAME)

if __name__ == '__main__':
    app.run(debug=True)
