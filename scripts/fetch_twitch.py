#!/usr/bin/env python3
"""
Twitch APIから配信情報を取得してdata/twitch.jsonに保存
"""
import os
import json
import requests
from datetime import datetime
from pathlib import Path

# 環境変数から取得
CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID')
CLIENT_SECRET = os.environ.get('TWITCH_CLIENT_SECRET')
CHANNEL_NAME = os.environ.get('TWITCH_CHANNEL', 'ikumin3')  # デフォルト値

# 出力先
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'
OUTPUT_FILE = DATA_DIR / 'twitch.json'


def get_access_token():
    """Client Credentials Flowでアクセストークン取得"""
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()['access_token']


def get_user_id(access_token, login):
    """ユーザー名からユーザーIDを取得"""
    url = 'https://api.twitch.tv/helix/users'
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {access_token}'
    }
    params = {'login': login}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()['data']
    if not data:
        raise ValueError(f'User not found: {login}')
    return data[0]['id'], data[0]


def get_videos(access_token, user_id, video_type='archive', limit=10):
    """過去の配信（アーカイブ）を取得"""
    url = 'https://api.twitch.tv/helix/videos'
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'user_id': user_id,
        'type': video_type,  # archive, highlight, upload
        'first': limit
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()['data']


def get_channel_info(access_token, user_id):
    """チャンネル情報を取得"""
    url = 'https://api.twitch.tv/helix/channels'
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {access_token}'
    }
    params = {'broadcaster_id': user_id}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()['data']
    return data[0] if data else {}


def format_video(video):
    """動画データを整形"""
    # サムネイルURLのプレースホルダーを置換
    thumbnail = video.get('thumbnail_url', '')
    thumbnail = thumbnail.replace('%{width}', '320').replace('%{height}', '180')

    return {
        'id': video['id'],
        'title': video['title'],
        'description': video.get('description', ''),
        'url': video['url'],
        'thumbnail': thumbnail,
        'duration': video['duration'],
        'view_count': video['view_count'],
        'created_at': video['created_at'],
        'type': video['type']
    }


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print('Error: TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET must be set')
        return 1

    print(f'Fetching Twitch data for channel: {CHANNEL_NAME}')

    # アクセストークン取得
    access_token = get_access_token()
    print('Got access token')

    # ユーザー情報取得
    user_id, user_info = get_user_id(access_token, CHANNEL_NAME)
    print(f'User ID: {user_id}')

    # チャンネル情報取得
    channel_info = get_channel_info(access_token, user_id)

    # 過去の配信取得
    videos = get_videos(access_token, user_id, limit=10)
    print(f'Found {len(videos)} videos')

    # データ整形
    result = {
        'channel': {
            'id': user_id,
            'login': user_info.get('login'),
            'display_name': user_info.get('display_name'),
            'profile_image': user_info.get('profile_image_url'),
            'description': user_info.get('description'),
            'url': f'https://twitch.tv/{CHANNEL_NAME}',
            'game_name': channel_info.get('game_name', ''),
            'tags': channel_info.get('tags', [])
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
