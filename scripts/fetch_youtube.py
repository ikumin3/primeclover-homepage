#!/usr/bin/env python3
"""
YouTube Data APIから動画情報を取得してdata/youtube.jsonに保存
"""
import os
import json
import requests
from datetime import datetime
from pathlib import Path

# 環境変数から取得
API_KEY = os.environ.get('YOUTUBE_API_KEY')
CHANNEL_ID = os.environ.get('YOUTUBE_CHANNEL_ID', 'UCUnUn31hUrjXkR-tGIlm0zA')

# 出力先
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'
OUTPUT_FILE = DATA_DIR / 'youtube.json'

BASE_URL = 'https://www.googleapis.com/youtube/v3'


def get_channel_info():
    """チャンネル情報を取得"""
    url = f'{BASE_URL}/channels'
    params = {
        'key': API_KEY,
        'id': CHANNEL_ID,
        'part': 'snippet,statistics'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()['items']
    if not data:
        raise ValueError(f'Channel not found: {CHANNEL_ID}')
    return data[0]


def get_videos(max_results=10):
    """チャンネルの動画一覧を取得"""
    # まずアップロード済み動画のプレイリストIDを取得
    url = f'{BASE_URL}/channels'
    params = {
        'key': API_KEY,
        'id': CHANNEL_ID,
        'part': 'contentDetails'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    uploads_playlist_id = response.json()['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # プレイリストから動画一覧を取得
    url = f'{BASE_URL}/playlistItems'
    params = {
        'key': API_KEY,
        'playlistId': uploads_playlist_id,
        'part': 'snippet',
        'maxResults': max_results
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()['items']


def format_video(item):
    """動画データを整形"""
    snippet = item['snippet']
    video_id = snippet['resourceId']['videoId']

    # サムネイルは高画質を優先
    thumbnails = snippet.get('thumbnails', {})
    thumbnail = (
        thumbnails.get('high', {}).get('url') or
        thumbnails.get('medium', {}).get('url') or
        thumbnails.get('default', {}).get('url', '')
    )

    return {
        'id': video_id,
        'title': snippet['title'],
        'description': snippet.get('description', '')[:200],
        'url': f'https://www.youtube.com/watch?v={video_id}',
        'thumbnail': thumbnail,
        'published_at': snippet['publishedAt']
    }


def main():
    if not API_KEY:
        print('Error: YOUTUBE_API_KEY must be set')
        return 1

    print(f'Fetching YouTube data for channel: {CHANNEL_ID}')

    # チャンネル情報取得
    channel = get_channel_info()
    snippet = channel['snippet']
    statistics = channel.get('statistics', {})
    print(f'Channel: {snippet["title"]}')

    # 動画一覧取得
    videos = get_videos(max_results=10)
    print(f'Found {len(videos)} videos')

    # データ整形
    result = {
        'channel': {
            'id': CHANNEL_ID,
            'title': snippet['title'],
            'description': snippet.get('description', ''),
            'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
            'url': f'https://www.youtube.com/channel/{CHANNEL_ID}',
            'subscriber_count': statistics.get('subscriberCount', '0'),
            'video_count': statistics.get('videoCount', '0')
        },
        'videos': [format_video(v) for v in videos],
        'updated_at': datetime.utcnow().isoformat() + 'Z'
    }

    # 出力
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f'Saved to {OUTPUT_FILE}')
    return 0


if __name__ == '__main__':
    exit(main())
