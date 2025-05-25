#!/usr/bin/env python3
"""
Google Fit APIからアクティビティデータを取得して保存
"""
import os
import json
import requests
from datetime import datetime, timedelta, timezone
from dateutil import parser
from auth import get_authenticated_session


def get_yesterday_date():
    """昨日の日付を取得"""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')


def get_time_range():
    """昨日の開始・終了時刻をナノ秒で取得"""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    start_time = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # ナノ秒に変換
    start_ns = int(start_time.timestamp() * 1000000000)
    end_ns = int(end_time.timestamp() * 1000000000)
    
    return start_ns, end_ns


def fetch_data_source_datasets(session, data_source_id, start_ns, end_ns):
    """指定されたデータソースからデータセットを取得"""
    url = f"https://www.googleapis.com/fitness/v1/users/me/dataSources/{data_source_id}/datasets/{start_ns}-{end_ns}"
    
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"データソース {data_source_id} の取得エラー: {e}")
        return None


def aggregate_fitness_data(session, start_ns, end_ns):
    """集計されたフィットネスデータを取得"""
    url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
    
    # 集計リクエストのペイロード
    payload = {
        "aggregateBy": [
            {"dataTypeName": "com.google.step_count.delta"},
            {"dataTypeName": "com.google.distance.delta"},
            {"dataTypeName": "com.google.calories.expended"},
            {"dataTypeName": "com.google.active_minutes"}
        ],
        "bucketByTime": {"durationMillis": 86400000},  # 1日（24時間）
        "startTimeMillis": start_ns // 1000000,
        "endTimeMillis": end_ns // 1000000
    }
    
    try:
        response = session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"集計データの取得エラー: {e}")
        return None


def parse_aggregate_data(aggregate_response):
    """集計レスポンスを解析してデータを抽出"""
    activity_data = {
        "steps": 0,
        "distance": 0.0,
        "calories": 0,
        "active_minutes": 0
    }
    
    if not aggregate_response or 'bucket' not in aggregate_response:
        return activity_data
    
    for bucket in aggregate_response['bucket']:
        for dataset in bucket.get('dataset', []):
            data_type = dataset.get('dataSourceId', '')
            
            for point in dataset.get('point', []):
                values = point.get('value', [])
                
                if 'step_count.delta' in data_type and values:
                    activity_data['steps'] += values[0].get('intVal', 0)
                
                elif 'distance.delta' in data_type and values:
                    # メートルをキロメートルに変換
                    activity_data['distance'] += values[0].get('fpVal', 0.0) / 1000
                
                elif 'calories.expended' in data_type and values:
                    activity_data['calories'] += values[0].get('fpVal', 0.0)
                
                elif 'active_minutes' in data_type and values:
                    activity_data['active_minutes'] += values[0].get('intVal', 0)
    
    # 小数点以下を適切に丸める
    activity_data['distance'] = round(activity_data['distance'], 2)
    activity_data['calories'] = round(activity_data['calories'])
    
    return activity_data


def save_activity_data(date_str, activity_data):
    """アクティビティデータをJSONファイルに保存"""
    # activityディレクトリが存在しない場合は作成
    os.makedirs('activity', exist_ok=True)
    
    # ファイルパス
    file_path = f"activity/{date_str}.json"
    
    # 保存するデータ
    data_to_save = {
        "date": date_str,
        "steps": activity_data['steps'],
        "distance": activity_data['distance'],
        "calories": activity_data['calories'],
        "active_minutes": activity_data['active_minutes'],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # JSONファイルに保存
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    
    print(f"アクティビティデータを保存しました: {file_path}")
    print(f"データ内容: {data_to_save}")
    
    return file_path


def main():
    """メイン処理"""
    print("=== Google Fit アクティビティデータ取得開始 ===")
    
    # 認証セッションを取得
    auth_result = get_authenticated_session()
    if not auth_result:
        print("認証に失敗しました")
        return False
    
    session, headers = auth_result
    
    # 昨日の日付と時間範囲を取得
    date_str = get_yesterday_date()
    start_ns, end_ns = get_time_range()
    
    print(f"取得対象日: {date_str}")
    
    # 集計データを取得
    aggregate_data = aggregate_fitness_data(session, start_ns, end_ns)
    
    if not aggregate_data:
        print("アクティビティデータの取得に失敗しました")
        return False
    
    # データを解析
    activity_data = parse_aggregate_data(aggregate_data)
    
    # ファイルに保存
    save_activity_data(date_str, activity_data)
    
    print("=== アクティビティデータ取得完了 ===")
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
