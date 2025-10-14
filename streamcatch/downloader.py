# Lógica de Download e Processamento de Vídeos

import os
import yt_dlp

def get_download_path():
    """Retorna o caminho da pasta 'Downloads/StreamCatch'."""
    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    path = os.path.join(downloads, "StreamCatch")
    os.makedirs(path, exist_ok=True)
    return path

def download_video(url: str):
    """Baixa o vídeo em MP4."""
    output_path = get_download_path()
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': False,
        'noprogress': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

def download_audio(url: str):
    """Baixa o áudio e converte para MP3."""
    output_path = get_download_path()
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'noprogress': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path
