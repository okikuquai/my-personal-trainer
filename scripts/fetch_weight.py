#!/usr/bin/env python3
"""
Google Fit APIから体重データを取得して保存
"""
import os
import json
import requests
from datetime import datetime, timedelta, timezone
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


def fetch_weight_data(session, start_ns, end_ns):
    """体重データを取得"""
    url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
    
    # 体重データの集計リクエスト
    payload = {
        "aggregateBy": [
            {"dataTypeName": "com.google.weight"}
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
        print(f"体重データの取得エラー: {e}")
        return None


def parse_weight_data(weight_response):
    """体重レスポンスを解析してデータを抽出"""
    weight_data = {
        "weight": None,
        "unit": "kg"
    }
    
    if not weight_response or 'bucket' not in weight_response:
        return weight_data
    
    # 最新の体重データを取得（複数ある場合は最後のもの）
    latest_weight = None
    latest_timestamp = 0
    
    for bucket in weight_response['bucket']:
        for dataset in bucket.get('dataset', []):
            data_type = dataset.get('dataSourceId', '')
            
            if 'weight' in data_type:
                for point in dataset.get('point', []):
                    values = point.get('value', [])
                    
                    if values:
                        # タイムスタンプを確認
                        start_time_ns = int(point.get('startTimeNanos', 0))
                        weight_value = values[0].get('fpVal', 0.0)
                        
                        if start_time_ns > latest_timestamp and weight_value > 0:
                            latest_timestamp = start_time_ns
                            latest_weight = weight_value
    
    if latest_weight is not None:
        weight_data['weight'] = round(latest_weight, 1)
    
    return weight_data


def fetch_weight_from_datasources(session, start_ns, end_ns):
    """データソースから直接体重データを取得（代替方法）"""
    # まずデータソース一覧を取得
    datasources_url = "https://www.googleapis.com/fitness/v1/users/me/dataSources"
    
    try:
        response = session.get(datasources_url)
        response.raise_for_status()
        datasources = response.json()
        
        weight_datasources = []
        for ds in datasources.get('dataSource', []):
            if ds.get('dataType', {}).get('name') == 'com.google.weight':
                weight_datasources.append(ds.get('dataStreamId'))
        
        print(f"体重データソースが見つかりました: {len(weight_datasources)}個")
        
        # 各データソースから体重データを取得
        latest_weight = None
        latest_timestamp = 0
        
        for ds_id in weight_datasources:
            dataset_url = f"https://www.googleapis.com/fitness/v1/users/me/dataSources/{ds_id}/datasets/{start_ns}-{end_ns}"
            
            try:
                ds_response = session.get(dataset_url)
                ds_response.raise_for_status()
                dataset = ds_response.json()
                
                for point in dataset.get('point', []):
                    values = point.get('value', [])
                    
                    if values:
                        start_time_ns = int(point.get('startTimeNanos', 0))
                        weight_value = values[0].get('fpVal', 0.0)
                        
                        if start_time_ns > latest_timestamp and weight_value > 0:
                            latest_timestamp = start_time_ns
                            latest_weight = weight_value
                            
            except requests.exceptions.RequestException as e:
                print(f"データソース {ds_id} の取得エラー: {e}")
                continue
        
        return {
            "weight": round(latest_weight, 1) if latest_weight else None,
            "unit": "kg"
        }
        
    except requests.exceptions.RequestException as e:
        print(f"データソース一覧の取得エラー: {e}")
        return {"weight": None, "unit": "kg"}


def save_weight_data(date_str, weight_data):
    """体重データをJSONファイルに保存"""
    # weightディレクトリが存在しない場合は作成
    os.makedirs('weight', exist_ok=True)
    
    # ファイルパス
    file_path = f"weight/{date_str}.json"
    
    # 体重データがない場合はファイルを作成しない
    if weight_data['weight'] is None:
        print(f"体重データがありません（{date_str}）")
        return None
    
    # 保存するデータ
    data_to_save = {
        "date": date_str,
        "weight": weight_data['weight'],
        "unit": weight_data['unit'],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # JSONファイルに保存
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    
    print(f"体重データを保存しました: {file_path}")
    print(f"データ内容: {data_to_save}")
    
    return file_path


def main():
    """メイン処理"""
    print("=== Google Fit 体重データ取得開始 ===")
    
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
    
    # 集計APIで体重データを取得
    weight_response = fetch_weight_data(session, start_ns, end_ns)
    weight_data = parse_weight_data(weight_response) if weight_response else {"weight": None, "unit": "kg"}
    
    # 集計APIでデータが取得できない場合、データソースから直接取得を試行
    if weight_data['weight'] is None:
        print("集計APIで体重データが見つからないため、データソースから直接取得を試行します...")
        weight_data = fetch_weight_from_datasources(session, start_ns, end_ns)
    
    # ファイルに保存
    saved_file = save_weight_data(date_str, weight_data)
    
    if saved_file:
        print("=== 体重データ取得完了 ===")
        return True
    else:
        print("=== 体重データが見つかりませんでした ===")
        return True  # エラーではないのでTrueを返す


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
