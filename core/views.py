from django.shortcuts import render
import yt_dlp
from django.http import JsonResponse, FileResponse
import threading
import re
from django.conf import settings
import os
# Create your views here.
progress_data = {
    "status":"",
    "downloaded": "0 MB",
    "total": "0 MB",
    "percentage": "0%",
    "filename": None,
}

def strip_ansi(text):
    return re.sub(r'\x1b\[[0-9;]*m', '', text) if text else '0%'
def home(request):
    global progress_data
    
    if request.method == 'POST':
        link = request.POST.get('link')

        def hook(d):
            if d['status'] == "downloading":
                progress_data["status"] = "Downloading"
                progress_data["downloaded"] = strip_ansi(d.get('_downloaded_bytes_str'))
                progress_data["total"] = strip_ansi(d.get('_total_bytes_str'))
                progress_data["percentage"] = strip_ansi(d.get('_percent_str'))
            elif d['status'] == "finished":
                progress_data['status'] = "Download completed"
                progress_data['filename'] = os.path.basename(d['filename'])
        def download():
            try:
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                ydl_opts = {
                    'outtmpl': os.path.join(settings.MEDIA_ROOT, '%(title)s.%(ext)s'),
                    'progress_hooks': [hook],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([link])
                
            except Exception as e:
                progress_data['status'] = "Error"
                progress_data["downloaded"] = "0 MB"
                progress_data["total"] = "0 MB"
                progress_data["percentage"] = "0%"

        threading.Thread(target=download).start()
        return JsonResponse({"message": "Download started"})
    
    return render(request, 'home.html')
def progress(request):
    return JsonResponse(progress_data)


def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    return JsonResponse({"error": "File not found"}, status=404)
