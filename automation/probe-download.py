"""One-video integration test for the website asset backup publisher."""
import pathlib
import shutil
import tempfile
import yt_dlp

path = pathlib.Path(tempfile.mkdtemp(prefix='video-backup-probe-'))
try:
    with yt_dlp.YoutubeDL({
        'quiet': True, 'no_warnings': True, 'noprogress': True, 'noplaylist': True,
        'socket_timeout': 20, 'retries': 0, 'extractor_retries': 0,
        'format': '137',
        'outtmpl': str(path / '%(id)s.%(ext)s'),
        'js_runtimes': {'node': {'path': shutil.which('node')}},
        'extractor_args': {'youtube': {'player_client': ['tv', 'web', 'ios', 'android_vr', 'visionos']}},
    }) as downloader:
        downloader.download(['https://www.youtube.com/watch?v=kzAfNg6pAvI'])
    files = list(path.glob('*.mp4'))
    assert len(files) == 1 and files[0].stat().st_size > 100000
    print('PROBE_DOWNLOAD_OK', files[0].stat().st_size)
finally:
    shutil.rmtree(path)
