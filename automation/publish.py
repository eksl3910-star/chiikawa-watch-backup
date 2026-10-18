"""Merge media staged in Korea and publish validated website backup assets."""
import datetime
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import urllib.request

BASE = 'https://chiikawa-backup-service.eksl3554.workers.dev'
TOKEN = os.environ['BACKUP_TOKEN'].strip()


def call(path, method='GET', data=None, headers=None):
    request = urllib.request.Request(BASE + path, data=data, method=method, headers={'Authorization': 'Bearer ' + TOKEN, 'User-Agent': 'ChiikawaBackupPublisher/1.0', **(headers or {})})
    return urllib.request.urlopen(request, timeout=180)


def api(path, method='GET', data=None, headers=None):
    with call(path, method, data, headers) as response:
        return json.load(response)


def main():
    probe = os.environ.get('BACKUP_PROBE') == 'true'
    jobs = [{'id': 'kzAfNg6pAvI', 'episode': 1}] if probe else api('/jobs')['episodes']
    for row in jobs:
        suffix = '?probe=1' if probe else ''
        prepared = api('/prepare/' + row['id'] + suffix, 'POST')
        if prepared.get('exists'):
            continue
        with tempfile.TemporaryDirectory(prefix='backup-publish-') as folder:
            root = pathlib.Path(folder)
            for part in ['video', 'audio']:
                path = root / part
                with call('/part/' + row['id'] + '/' + part) as response, path.open('wb') as output:
                    shutil.copyfileobj(response, output)
                if path.stat().st_size != prepared['parts'][part]['bytes'] or hashlib.md5(path.read_bytes()).hexdigest() != prepared['parts'][part]['etag']:
                    raise ValueError('Staged media checksum mismatch')
            result = root / 'episode.mp4'
            subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(root / 'video'), '-i', str(root / 'audio'), '-c', 'copy', '-movflags', '+faststart', str(result)], check=True)
            output = subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(result)])
            info = json.loads(output)
            if not 59 <= float(info['format']['duration']) <= 180:
                raise ValueError('Unexpected merged duration')
            video = next(s for s in info['streams'] if s['codec_type'] == 'video')
            audio = next(s for s in info['streams'] if s['codec_type'] == 'audio')
            if video['codec_name'] != 'h264' or audio['codec_name'] != 'aac' or video['height'] != prepared['height']:
                raise ValueError('Unexpected merged codecs or quality')
            data = result.read_bytes()
            if len(data) > 60_000_000:
                raise ValueError('Merged file too large')
            md5 = hashlib.md5(data).hexdigest()
            published = api('/publish/' + row['id'] + suffix, 'POST', data, {'Content-Type': 'video/mp4', 'X-Video-MD5': md5})
            if published['md5'] != md5 or published['bytes'] != len(data):
                raise ValueError('Published checksum mismatch')
            print(('BACKUP_PROBE_OK' if probe else 'BACKED_UP'), 'episode=' + str(row['episode']), 'height=' + str(video['height']), 'bytes=' + str(len(data)), flush=True)
    status = api('/complete' + ('?probe=1' if probe else ''), 'POST')
    if not status['ok']:
        raise ValueError('Missing backups: ' + str(status['missing']))
    return {**status, 'probe': probe, 'publishedThisRun': len(jobs)}


if __name__ == '__main__':
    try:
        report = main()
    except Exception as error:
        report = {'ok': False, 'checkedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'error': str(error)[:200]}
        pathlib.Path('backup-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        raise
    pathlib.Path('backup-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report), flush=True)
