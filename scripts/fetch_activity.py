#!/usr/bin/env python3
"""
Android Health Connectからアクティビティデータを取得して保存するのだ！

現在はモックアップ実装だが、将来的には実際のHealth Connect APIを使用するのだ。
"""
import os
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from health_connect_client import create_health_connect_client, StepsRecord, DistanceRecord, CaloriesRecord


# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_yesterday_date():
    """昨日の日付を取得するのだ"""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')


def get_time_range():
    """昨日の開始・終了時刻を取得するのだ"""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    start_time = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return start_time, end_time


def fetch_activity_data_from_health_connect(client, start_time, end_time):
    """
    Health Connectからアクティビティデータを取得するのだ
    
    Args:
        client: Health Connectクライアント
        start_time: 開始日時
        end_time: 終了日時
        
    Returns:
        アクティビティデータの辞書
    """
    logger.info(f"Health Connectからアクティビティデータを取得中... ({start_time} - {end_time})")
    
    activity_data = {
        "steps": 0,
        "distance_meters": 0.0,
        "active_calories": 0.0,
        "total_calories": 0.0,
        "heart_rate": {
            "average": 0,
            "max": 0,
            "min": 0
        }
    }
    
    try:
        # 歩数データを取得
        steps_records = client.read_steps_data(start_time, end_time)
        if steps_records:
            activity_data["steps"] = sum(record.steps for record in steps_records)
            logger.info(f"歩数データ取得完了: {activity_data['steps']}歩")
        
        # 距離データを取得（モックモードでは歩数から計算）
        if activity_data["steps"] > 0:
            # 平均的な歩幅を0.7mとして距離を推定
            activity_data["distance_meters"] = round(activity_data["steps"] * 0.7, 1)
            logger.info(f"距離データ算出完了: {activity_data['distance_meters']}m")
        
        # カロリーデータを取得（モックモードでは歩数から推定）
        if activity_data["steps"] > 0:
            # 1000歩あたり約40kcalとして推定
            activity_data["active_calories"] = round(activity_data["steps"] * 0.04, 1)
            activity_data["total_calories"] = round(activity_data["active_calories"] * 5, 1)  # 基礎代謝込み
            logger.info(f"カロリーデータ算出完了: アクティブ{activity_data['active_calories']}kcal, 総計{activity_data['total_calories']}kcal")
        
        # 心拍数データを取得（モックモードでは固定値）
        import random
        if activity_data["steps"] > 5000:  # 活動的だった場合
            activity_data["heart_rate"] = {
                "average": random.randint(70, 85),
                "max": random.randint(120, 160),
                "min": random.randint(60, 70)
            }
        else:
            activity_data["heart_rate"] = {
                "average": random.randint(65, 75),
                "max": random.randint(90, 120),
                "min": random.randint(55, 65)
            }
        
        logger.info(f"心拍数データ算出完了: 平均{activity_data['heart_rate']['average']}bpm")
        
    except Exception as e:
        logger.error(f"Health Connectからのデータ取得中にエラーが発生したのだ: {e}")
        
    return activity_data


def save_activity_data(date_str, activity_data):
    """
    アクティビティデータをJSONファイルに保存するのだ
    
    Args:
        date_str: 日付文字列
        activity_data: アクティビティデータ
        
    Returns:
        保存したファイルパス
    """
    # activityディレクトリが存在しない場合は作成
    activity_dir = Path('activity')
    activity_dir.mkdir(exist_ok=True)
    
    # ファイルパス
    file_path = activity_dir / f"{date_str}.json"
    
    # 保存するデータ（Health Connect形式）
    data_to_save = {
        "date": date_str,
        "steps": activity_data['steps'],
        "distance_meters": activity_data['distance_meters'],
        "active_calories": activity_data['active_calories'],
        "total_calories": activity_data['total_calories'],
        "heart_rate": activity_data['heart_rate'],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "data_source": "health_connect"
    }
    
    # JSONファイルに保存
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        
        logger.info(f"アクティビティデータを保存したのだ: {file_path}")
        logger.info(f"データ内容: {data_to_save}")
        
        return str(file_path)
        
    except Exception as e:
        logger.error(f"ファイル保存中にエラーが発生したのだ: {e}")
        return None


def validate_health_connect_permissions(client):
    """
    Health Connectの権限を確認するのだ
    
    Args:
        client: Health Connectクライアント
        
    Returns:
        権限が正常かどうか
    """
    required_permissions = [
        "READ_STEPS",
        "READ_DISTANCE", 
        "READ_TOTAL_CALORIES_BURNED",
        "READ_ACTIVE_CALORIES_BURNED",
        "READ_HEART_RATE"
    ]
    
    permissions = client.check_permissions(required_permissions)
    
    missing_permissions = [perm for perm, granted in permissions.items() if not granted]
    
    if missing_permissions:
        logger.warning(f"以下の権限が不足しているのだ: {missing_permissions}")
        return False
    
    logger.info("Health Connectの権限確認完了なのだ")
    return True


def main():
    """メイン処理なのだ"""
    logger.info("=== Health Connect アクティビティデータ取得開始 ===")
    
    try:
        # Health Connectクライアントを作成（現在はモックモード）
        client = create_health_connect_client(mock_mode=True)
        
        # 権限を確認
        if not validate_health_connect_permissions(client):
            logger.error("Health Connectの権限が不足しているのだ")
            return False
        
        # 昨日の日付と時間範囲を取得
        date_str = get_yesterday_date()
        start_time, end_time = get_time_range()
        
        logger.info(f"取得対象日: {date_str}")
        logger.info(f"時間範囲: {start_time} - {end_time}")
        
        # Health Connectからアクティビティデータを取得
        activity_data = fetch_activity_data_from_health_connect(client, start_time, end_time)
        
        if not activity_data or activity_data['steps'] == 0:
            logger.warning("有効なアクティビティデータが取得できなかったのだ")
            # それでもファイルは作成する（0歩の日もある）
        
        # ファイルに保存
        saved_file = save_activity_data(date_str, activity_data)
        
        if saved_file:
            logger.info("=== アクティビティデータ取得完了 ===")
            return True
        else:
            logger.error("データ保存に失敗したのだ")
            return False
            
    except Exception as e:
        logger.error(f"処理中に予期しないエラーが発生したのだ: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
